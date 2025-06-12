// src/pages/ProfilePage.jsx
import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { toast } from "react-hot-toast";
import {
  UserIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  ArrowLeftIcon,
} from "@heroicons/react/24/outline";
import { Link, useNavigate } from "react-router-dom";

import { profileAPI } from "../utils/api";
import { useAuth } from "../context/AuthContext";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Select from "../components/ui/Select";
import Card from "../components/ui/Card";
import Loading from "../components/ui/Loading";

const ProfilePage = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({});
  const navigate = useNavigate();

  const activityLevelOptions = [
    { value: "sedentary", label: "Sedentary (Little to no exercise)" },
    { value: "light", label: "Light (Exercise 1-3 days/week)" },
    { value: "moderate", label: "Moderate (Exercise 3-5 days/week)" },
    { value: "active", label: "Active (Exercise 6-7 days/week)" },
    { value: "very_active", label: "Very Active (2x/day or intense exercise)" },
  ];

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await profileAPI.get();
      setProfile(response.data.profile);
      setFormData(response.data.profile);
    } catch (error) {
      toast.error("Failed to fetch profile");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    setEditing(true);
    setFormData(profile);
  };

  const handleCancel = () => {
    setEditing(false);
    setFormData(profile);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await profileAPI.update(formData);
      setProfile(formData);
      setEditing(false);
      toast.success("Profile updated successfully! 🎉");
    } catch (error) {
      toast.error("Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const resetProfile = async () => {
    if (window.confirm("Are you sure you want to reset your profile? This action cannot be undone.")) {
      try {
        const response = await profileAPI.post("/api/profile/reset");
        if (response.status === 200) {
          toast.success("Profile reset successfully");
          navigate("/setup");
        }
      } catch (error) {
        console.error("Error resetting profile:", error);
        toast.error("Failed to reset profile");
      }
    }
  };

  if (loading) {
    return <Loading fullScreen message="Loading your profile..." />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-8"
        >
          <div className="flex items-center">
            <Link
              to="/dashboard"
              className="mr-4 p-2 rounded-lg hover:bg-white/50 transition-colors"
            >
              <ArrowLeftIcon className="w-5 h-5 text-gray-600" />
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Profile Settings
              </h1>
              <p className="text-gray-600">
                Manage your personal information and preferences
              </p>
            </div>
          </div>

          {!editing && (
            <Button onClick={handleEdit}>
              <PencilIcon className="w-5 h-5" />
              Edit Profile
            </Button>
          )}
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Profile Summary Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-1"
          >
            <Card>
              <div className="text-center">
                <div className="w-24 h-24 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <UserIcon className="w-12 h-12 text-white" />
                </div>

                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  {user?.username}
                </h2>
                <p className="text-gray-500 mb-4">{user?.email}</p>

                {profile && (
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Age:</span>
                      <span className="font-medium">{profile.age} years</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Gender:</span>
                      <span className="font-medium capitalize">
                        {profile.gender}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Current Weight:</span>
                      <span className="font-medium">{profile.weight} kg</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Goal Weight:</span>
                      <span className="font-medium">
                        {profile.goal_weight} kg
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          </motion.div>

          {/* Profile Details */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-2"
          >
            <Card>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  Personal Information
                </h3>

                {editing && (
                  <div className="flex space-x-2">
                    <Button variant="ghost" size="sm" onClick={handleCancel}>
                      <XMarkIcon className="w-4 h-4" />
                      Cancel
                    </Button>
                    <Button size="sm" onClick={handleSave} loading={saving}>
                      <CheckIcon className="w-4 h-4" />
                      Save Changes
                    </Button>
                  </div>
                )}
              </div>

              {profile && (
                <div className="grid md:grid-cols-2 gap-6">
                  <Input
                    label="Age"
                    type="number"
                    value={editing ? formData.age : profile.age}
                    onChange={(e) => handleChange("age", e.target.value)}
                    disabled={!editing}
                  />

                  <Select
                    label="Gender"
                    value={editing ? formData.gender : profile.gender}
                    onChange={(e) => handleChange("gender", e.target.value)}
                    options={[
                      { value: "male", label: "Male" },
                      { value: "female", label: "Female" },
                    ]}
                    disabled={!editing}
                  />

                  <Input
                    label="Current Weight (kg)"
                    type="number"
                    value={editing ? formData.weight : profile.weight}
                    onChange={(e) => handleChange("weight", e.target.value)}
                    disabled={!editing}
                  />

                  <Input
                    label="Height (cm)"
                    type="number"
                    value={editing ? formData.height : profile.height}
                    onChange={(e) => handleChange("height", e.target.value)}
                    disabled={!editing}
                  />

                  <Input
                    label="Goal Weight (kg)"
                    type="number"
                    value={editing ? formData.goal_weight : profile.goal_weight}
                    onChange={(e) =>
                      handleChange("goal_weight", e.target.value)
                    }
                    disabled={!editing}
                  />

                  <Select
                    label="Activity Level"
                    value={
                      editing ? formData.activity_level : profile.activity_level
                    }
                    onChange={(e) =>
                      handleChange("activity_level", e.target.value)
                    }
                    options={activityLevelOptions}
                    disabled={!editing}
                  />
                </div>
              )}

              {/* BMI Calculator */}
              {profile && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl"
                >
                  <h4 className="font-semibold text-gray-900 mb-4">
                    Health Metrics
                  </h4>

                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {(profile.weight / (profile.height / 100) ** 2).toFixed(
                          1
                        )}
                      </div>
                      <div className="text-sm text-gray-600">Current BMI</div>
                    </div>

                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {(
                          profile.goal_weight /
                          (profile.height / 100) ** 2
                        ).toFixed(1)}
                      </div>
                      <div className="text-sm text-gray-600">Goal BMI</div>
                    </div>

                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {Math.abs(profile.weight - profile.goal_weight).toFixed(
                          1
                        )}{" "}
                        kg
                      </div>
                      <div className="text-sm text-gray-600">
                        {profile.weight > profile.goal_weight
                          ? "To Lose"
                          : "To Gain"}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              <Button 
                variant="outlined" 
                color="error" 
                onClick={resetProfile}
                sx={{ mt: 2 }}
              >
                Reset Profile
              </Button>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
