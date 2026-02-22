from core.response import (    
    OutletObject,    
    OutletObjectsUser,
    OutletSliderImageObject,
    FranchiseObject,
    FranchiseObjects,    
    OutletCreationResponse,
    OutletObjects,
    FeatureResponse, # Will be used for GlobalFeature
    OutletFeatureRequestResponse,
    UserResponse,
    OutletResponse,
    OutletActiveFeatureResponse
)

from core.request import (
    FranchiseCreationRequest,
    OutletCreationRequest,
    OutletFeatureRequestCreateRequest,
    OutletFeatureRequestUpdateRequest,
    FeaturePriceUpdateRequest
)

from .models import Franchise, Outlet, OutletSliderImage, GlobalFeature, OutletFeature, OutletFeatureRequest, get_user_model
from fastapi import HTTPException, status
from core.utils.asyncs import get_queryset
from django.db.models import Prefetch
from django.db import transaction
from typing import List, Optional
from asgiref.sync import sync_to_async

User = get_user_model()


class RestaurantService:
    # ... existing RestaurantService methods ...
    async def create_franchise(self, body: FranchiseCreationRequest):
        try:
            name = body.name
            franchise = Franchise(name=name)
            await franchise.asave()
            return FranchiseObject(
                name=franchise.name,
                slug=franchise.slug
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create franchise: {str(e)}"
            )
            
    async def get_franchise(self, slug: str, limit: int | None, last_seen_id: int | None) -> FranchiseObject | FranchiseObjects:
        if slug == "__all__":
            try:                            
                queryset = Franchise.objects.order_by("id")                
                if last_seen_id is not None:
                    queryset = queryset.filter(id__gt=last_seen_id)
                                                    
                if limit is not None:
                    queryset = queryset[:limit]

                franchises = await get_queryset(list, queryset)
                last_seen_id = franchises[-1].id if franchises else None
                return FranchiseObjects(
                    last_seen_id=last_seen_id,
                    franchises=[
                        FranchiseObject(name=f.name, slug=f.slug) for f in franchises
                    ]
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve franchises: {str(e)}"
                )
        else:
            try:
                franchise = await Franchise.objects.aget(slug=slug)
                return FranchiseObject(
                    name=franchise.name,
                    slug=franchise.slug
                )
            except Franchise.DoesNotExist:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Franchise not found."
                )

    async def create_outlet(self, body: OutletCreationRequest, franchise, cover_image=None, mid_page_slider=None) -> OutletCreationResponse:
        try:            
            name = body.name
            outlet = await Outlet.objects.acreate(
                name=name,
                franchise=franchise
            )
            # Save cover image if provided
            slider_objs = []
            if cover_image:
                outlet.cover_image.save(cover_image.name, cover_image, save=False)
                await outlet.asave()
            # Save slider images if provided
            if mid_page_slider:
                from .models import OutletSliderImage
                for idx, slider_file in enumerate(mid_page_slider):
                    slider_obj = await OutletSliderImage.objects.acreate(
                        outlet=outlet,
                        order=idx
                    )
                    slider_obj.image.save(slider_file.name, slider_file, save=False)
                    await slider_obj.asave()
                    slider_objs.append(slider_obj)
            # Prepare response
            from .response import OutletSliderImageObject
            slider_response = [OutletSliderImageObject(image=img.image.url, order=img.order) for img in slider_objs] if slider_objs else None
            return OutletCreationResponse(
                name=outlet.name,
                slug=str(outlet.slug) if outlet.slug else "",
                cover_image=outlet.cover_image.url if outlet.cover_image else None,
                mid_page_slider=slider_response
            )
        except Franchise.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Franchise does not exist."
            )
        except Exception as e:                        
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create outlet: {str(e)}"
            )
            
    async def get_outlet(self, slug: str, franchise, limit: int | None, last_seen_id: int | None) -> OutletObject | OutletObjects:        
        try:
            if slug == "__all__":
                queryset = Outlet.objects.filter(franchise=franchise).order_by("id")
                if last_seen_id is not None:
                    queryset = queryset.filter(id__gt=last_seen_id)
                if limit is not None:
                    queryset = queryset[:limit]
                outlets = await get_queryset(list, queryset)
                last_seen_id = outlets[-1].id if outlets else None
                outlet_objs = []
                for o in outlets:
                    slider_imgs = await get_queryset(list, OutletSliderImage.objects.filter(outlet=o).order_by("order"))
                    slider_response = [OutletSliderImageObject(image=img.image.url, order=img.order) for img in slider_imgs] if slider_imgs else None
                    outlet_objs.append(
                        OutletObject(
                            name=o.name,
                            slug=o.slug,
                            cover_image=o.cover_image.url if o.cover_image else None,
                            mid_page_slider=slider_response
                        )
                    )
                return OutletObjects(
                    last_seen_id=last_seen_id,
                    outlets=outlet_objs
                )
            else:
                try:
                    outlet = await Outlet.objects.aget(slug=slug, franchise=franchise)
                    slider_imgs = await get_queryset(list, OutletSliderImage.objects.filter(outlet=outlet).order_by("order"))
                    slider_response = [OutletSliderImageObject(image=img.image.url, order=img.order) for img in slider_imgs] if slider_imgs else None
                    return OutletObject(
                        name=outlet.name,
                        slug=outlet.slug,
                        cover_image=outlet.cover_image.url if outlet.cover_image else None,
                        mid_page_slider=slider_response
                    )
                except Outlet.DoesNotExist:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Outlet not found."
                    )
        except Franchise.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Franchise not found."
            )
            
    # public
    async def get_user_outlets(self, franchise) -> OutletObjectsUser:
        try:            
            outlet_objs = []
            slider_prefetch = Prefetch("slider_images",queryset=OutletSliderImage.objects.order_by("order"))
            async for o in Outlet.objects.prefetch_related(slider_prefetch).filter(franchise=franchise):                
                slider_images = []
                async for img in o.slider_images.all():
                    slider_images.append(OutletSliderImageObject(image=img.image.url, order=img.order))
                outlet_objs.append(
                    OutletObject(
                        name=o.name,
                        slug=str(o.slug) if o.slug else "",
                        cover_image=o.cover_image.url if o.cover_image else None,
                        mid_page_slider=slider_images if slider_images else None
                    )
                )
            return OutletObjectsUser(
                outlets=outlet_objs
            )
        except Exception as e:            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve user outlets: {str(e)}"
            )


class FeatureService:
    async def list_available_master_features(self) -> List[FeatureResponse]:
        """
        Lists all GlobalFeature objects. This is the master list of available features.
        """
        features = []
        async for f in GlobalFeature.objects.all():
            features.append(FeatureResponse(
                name=f.name,
                description=f.description,
                slug=f.slug,
                price=None # Price is per-subscription, not global
            ))
        return features

    async def list_outlet_active_features(self, outlet: Outlet) -> List[OutletActiveFeatureResponse]:
        """
        Lists all active features for a specific outlet, including their custom prices.
        """
        active_features = []
        # Query OutletFeature directly as it contains the price and links to GlobalFeature
        async for of in OutletFeature.objects.filter(outlet=outlet).select_related('global_feature'):
            active_features.append(OutletActiveFeatureResponse(
                name=of.global_feature.name,
                description=of.global_feature.description,
                price=of.price,
                slug=of.global_feature.slug
            ))
        return active_features

    async def create_feature_request(self, outlet: Outlet, request_data: OutletFeatureRequestCreateRequest, requested_by_user: User) -> OutletFeatureRequestResponse:
        global_features = await get_queryset(list, GlobalFeature.objects.filter(slug__in=request_data.feature_slugs))
        if not global_features:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No valid global features found for the provided slugs.")
        
        # Get currently active features for the outlet
        active_outlet_features = await get_queryset(list, OutletFeature.objects.filter(outlet=outlet).select_related('global_feature'))
        active_feature_slugs = {of.global_feature.slug for of in active_outlet_features}

        for requested_slug in request_data.feature_slugs:
            if request_data.request_type == 'add':
                if requested_slug in active_feature_slugs:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Feature '{requested_slug}' is already enabled for this outlet.")
            elif request_data.request_type == 'remove':
                if requested_slug not in active_feature_slugs:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Feature '{requested_slug}' is not currently enabled for this outlet.")

        feature_request = await sync_to_async(self._perform_create_feature_request_sync)(
            outlet, request_data, requested_by_user, global_features
        )
            
        return await self._get_feature_request_response(feature_request)

    def _perform_create_feature_request_sync(self, outlet: Outlet, request_data: OutletFeatureRequestCreateRequest, requested_by_user: User, global_features: List[GlobalFeature]) -> OutletFeatureRequest:
        with transaction.atomic():
            feature_request = OutletFeatureRequest.objects.create(
                outlet=outlet,
                status='pending',
                request_type=request_data.request_type,
                requested_by=requested_by_user,
                note=request_data.note
            )
            feature_request.features.set(global_features)
            return feature_request

    async def _get_feature_request_response(self, feature_request: OutletFeatureRequest) -> OutletFeatureRequestResponse:
        """
        Constructs the response for a feature request, showing GLOBAL features in the request
        and the CURRENT active subscriptions for the outlet.
        """
        feature_request = await OutletFeatureRequest.objects.select_related(
            'outlet', 'requested_by', 'approved_by'
        ).prefetch_related('features').aget(id=feature_request.id)

        # Features linked to the request are GlobalFeatures
        requested_global_features = [
            FeatureResponse(name=f.name, description=f.description, slug=f.slug)
            async for f in feature_request.features.all()
        ]

        return OutletFeatureRequestResponse(
            id=feature_request.id,
            outlet=OutletResponse(name=feature_request.outlet.name, slug=feature_request.outlet.slug),
            features=requested_global_features, # Shows what was in the request
            status=feature_request.status,
            request_type=feature_request.request_type,
            requested_by=UserResponse(email=feature_request.requested_by.email) if feature_request.requested_by else None,
            approved_by=UserResponse(email=feature_request.approved_by.email) if feature_request.approved_by else None,
            created_at=feature_request.created_at,
            updated_at=feature_request.updated_at,
            note=feature_request.note
        )

    async def list_outlet_feature_requests(self, outlet: Outlet) -> List[OutletFeatureRequestResponse]:
        feature_requests = []
        async for fr in OutletFeatureRequest.objects.filter(outlet=outlet).order_by('-created_at'):
            feature_requests.append(await self._get_feature_request_response(fr))
        return feature_requests

    async def list_all_feature_requests(self, status_filter: Optional[str] = None) -> List[OutletFeatureRequestResponse]:
        qs = OutletFeatureRequest.objects.all().order_by('-created_at')
        if status_filter:
            qs = qs.filter(status=status_filter)
        
        feature_requests = []
        async for fr in qs:
            feature_requests.append(await self._get_feature_request_response(fr))
        return feature_requests

    async def update_feature_request(self, request_id: int, update_data: OutletFeatureRequestUpdateRequest, approved_by_user: User) -> OutletFeatureRequestResponse:
        try:
            feature_request = await OutletFeatureRequest.objects.select_related('outlet').aget(id=request_id)
        except OutletFeatureRequest.DoesNotExist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature Request not found.")

        if feature_request.status != 'pending':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending requests can be updated.")
        
        updated_feature_request = await sync_to_async(self._perform_update_feature_request_sync)(
            feature_request, update_data, approved_by_user
        )

        return await self._get_feature_request_response(updated_feature_request)

    def _perform_update_feature_request_sync(self, feature_request: OutletFeatureRequest, update_data: OutletFeatureRequestUpdateRequest, approved_by_user: User) -> OutletFeatureRequest:
        with transaction.atomic():
            feature_request.status = update_data.status
            feature_request.note = update_data.note
            feature_request.approved_by = approved_by_user
            feature_request.save() # Triggers the signal

            if feature_request.status == 'approved' and update_data.feature_prices:
                outlet = feature_request.outlet
                for price_update in update_data.feature_prices:
                    try:
                        subscription = OutletFeature.objects.get( # Synchronous get
                            outlet=outlet,
                            global_feature__slug=price_update.feature_slug
                        )
                        subscription.price = price_update.price
                        subscription.save() # Synchronous save
                    except OutletFeature.DoesNotExist:
                        print(f"Warning: Subscription for '{price_update.feature_slug}' not found for outlet '{outlet.slug}' during price update. Signal might not have run or feature was not in request.")
                        pass
            return feature_request
