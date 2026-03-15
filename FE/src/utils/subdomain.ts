export const getSubdomain = () => {
  const host = window.location.hostname;
  
  // --- LOCAL DEV OVERRIDE ---
  // Change 'admin' to 'dominos' or null to test different views on localhost:5173
  const LOCAL_DEV_OVERRIDE: string | null = 'admin'; 

  if (host === 'localhost' || host === '127.0.0.1') {
    return LOCAL_DEV_OVERRIDE;
  }
  // ---------------------------

  if (host.endsWith('.lvh.me')) {
    const parts = host.split('.');
    if (parts.length > 2) {
      return parts[0];
    }
    return null;
  }

  // Production mapping for dishto.in
  const parts = host.split('.');
  if (parts.length > 2) {
    return parts[0];
  }
  
  return null;
};

export const isSuperAdmin = () => getSubdomain() === 'admin';
export const isFranchise = () => {
  const sub = getSubdomain();
  return sub !== null && sub !== 'admin';
};
