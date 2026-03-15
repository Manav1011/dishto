export const getSubdomain = () => {
  const host = window.location.hostname;
  
  // Handle local development with subdomains (lvh.me)
  if (host.endsWith('.lvh.me')) {
    const parts = host.split('.');
    if (parts.length > 2) {
      return parts[0];
    }
    return null;
  }

  // Production/Staging mapping for dishto.in
  const parts = host.split('.');
  
  // Example: admin.dishto.in (3 parts)
  // Example: ldce.dishto.in (3 parts)
  // Example: dishto.in (2 parts)
  if (parts.length > 2) {
    // If the last two parts are dishto.in, then the first part is the subdomain
    if (parts[parts.length - 2] === 'dishto' && parts[parts.length - 1] === 'in') {
      return parts[0];
    }
  }
  
  return null;
};

export const isSuperAdmin = () => getSubdomain() === 'admin';
export const isFranchise = () => {
  const sub = getSubdomain();
  return sub !== null && sub !== 'admin';
};
