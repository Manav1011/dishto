import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../api';
import { 
  User, 
  Mail, 
  Phone, 
  Lock, 
  ShieldCheck, 
  Save, 
  Loader2, 
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

const ProfileSettings = () => {
  const { user, refreshUser } = useAuth();
  
  // Profile State
  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    ph_no: user?.ph_no || ''
  });
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState(false);

  // Password State
  const [passwords, setPasswords] = useState({
    old_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileLoading(true);
    setProfileSuccess(false);
    try {
      await api.post('/protected/auth/update-profile', profileData);
      await refreshUser();
      setProfileSuccess(true);
      setTimeout(() => setProfileSuccess(false), 3000);
    } catch (err) {
      console.error('Profile update failed', err);
    } finally {
      setProfileLoading(false);
    }
  };

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passwords.new_password !== passwords.confirm_password) {
      setPasswordError('New passwords do not match');
      return;
    }
    
    setPasswordLoading(true);
    setPasswordError('');
    setPasswordSuccess(false);
    try {
      await api.post('/protected/auth/update-password', {
        old_password: passwords.old_password,
        new_password: passwords.new_password
      });
      setPasswordSuccess(true);
      setPasswords({ old_password: '', new_password: '', confirm_password: '' });
      setTimeout(() => setPasswordSuccess(false), 3000);
    } catch (err: any) {
      setPasswordError(err.response?.data?.message || 'Failed to update password. Ensure your old password is correct.');
    } finally {
      setPasswordLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-[1000px] mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="mb-12">
        <h1 className="text-4xl font-brand font-bold text-slate-900 flex items-center gap-3">
          <ShieldCheck className="w-10 h-10 text-orange-500" />
          Account Settings
        </h1>
        <p className="text-slate-500 mt-2 text-lg font-medium">Manage your administrative profile and security credentials.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        
        {/* Profile Information */}
        <section className="space-y-6">
          <div className="flex items-center gap-2 px-1">
            <User className="w-5 h-5 text-orange-500" />
            <h3 className="font-brand font-bold text-xl text-slate-800">Profile Information</h3>
          </div>
          
          <div className="bg-white rounded-[2.5rem] border border-slate-200 p-8 shadow-xl shadow-slate-200/50">
            <form onSubmit={handleUpdateProfile} className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Full Name</label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300" />
                  <input 
                    type="text"
                    value={profileData.name}
                    onChange={(e) => setProfileData({...profileData, name: e.target.value})}
                    placeholder="Master Admin"
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 transition-all font-medium"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300" />
                  <input 
                    type="email"
                    value={profileData.email}
                    onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 transition-all font-medium"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Phone Number</label>
                <div className="relative">
                  <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300" />
                  <input 
                    type="tel"
                    value={profileData.ph_no}
                    onChange={(e) => setProfileData({...profileData, ph_no: e.target.value})}
                    placeholder="+1 (555) 000-0000"
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 transition-all font-medium"
                  />
                </div>
              </div>

              <button 
                type="submit"
                disabled={profileLoading}
                className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold flex items-center justify-center gap-2 orange-glow tactile disabled:opacity-50"
              >
                {profileLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                  profileSuccess ? <CheckCircle2 className="w-5 h-5 text-emerald-400" /> : <Save className="w-5 h-5" />
                )}
                {profileSuccess ? 'Profile Updated' : 'Save Changes'}
              </button>
            </form>
          </div>
        </section>

        {/* Security / Password */}
        <section className="space-y-6">
          <div className="flex items-center gap-2 px-1">
            <Lock className="w-5 h-5 text-orange-500" />
            <h3 className="font-brand font-bold text-xl text-slate-800">Security Credentials</h3>
          </div>

          <div className="bg-white rounded-[2.5rem] border border-slate-200 p-8 shadow-xl shadow-slate-200/50">
            {passwordError && (
              <div className="mb-6 p-4 bg-rose-50 text-rose-600 rounded-2xl text-xs border border-rose-100 flex items-center gap-3">
                <AlertCircle className="w-4 h-4" />
                {passwordError}
              </div>
            )}

            <form onSubmit={handleUpdatePassword} className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Current Password</label>
                <input 
                  type="password"
                  required
                  value={passwords.old_password}
                  onChange={(e) => setPasswords({...passwords, old_password: e.target.value})}
                  className="w-full px-6 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 transition-all font-medium"
                />
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">New Password</label>
                <input 
                  type="password"
                  required
                  value={passwords.new_password}
                  onChange={(e) => setPasswords({...passwords, new_password: e.target.value})}
                  className="w-full px-6 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 transition-all font-medium"
                />
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Confirm New Password</label>
                <input 
                  type="password"
                  required
                  value={passwords.confirm_password}
                  onChange={(e) => setPasswords({...passwords, confirm_password: e.target.value})}
                  className="w-full px-6 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500/50 transition-all font-medium"
                />
              </div>

              <button 
                type="submit"
                disabled={passwordLoading}
                className="w-full py-4 bg-orange-500 text-white rounded-2xl font-bold flex items-center justify-center gap-2 orange-glow tactile disabled:opacity-50"
              >
                {passwordLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                  passwordSuccess ? <CheckCircle2 className="w-5 h-5" /> : <Lock className="w-5 h-5" />
                )}
                {passwordSuccess ? 'Password Changed' : 'Update Credentials'}
              </button>
            </form>
          </div>
        </section>
      </div>
    </div>
  );
};

export default ProfileSettings;
