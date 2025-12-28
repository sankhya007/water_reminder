[buildozer]
log_level = 2

[app]
# --------------------------------------------------
# App identity
# --------------------------------------------------
title = WaterReminder
package.name = waterreminder
package.domain = org.example

# --------------------------------------------------
# Source
# --------------------------------------------------
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,ttf,mp3

version = 0.1

# --------------------------------------------------
# Python / Kivy
# --------------------------------------------------
requirements = python3,kivy,pyjnius

orientation = portrait
fullscreen = 1

# --------------------------------------------------
# Android configuration (CRITICAL)
# --------------------------------------------------

# MUST match what you install in GitHub Actions
android.api = 34
android.minapi = 21
android.build_tools_version = 36.1.0

# Force Buildozer to use the correct SDK/NDK
android.sdk_path = /home/runner/android-sdk
android.ndk_path = /home/runner/android-sdk/ndk/25.2.9519653

# Permissions
android.permissions = POST_NOTIFICATIONS,WAKE_LOCK

android.allow_backup = True

# App icon
android.icon.filename = assets/icon.png

# --------------------------------------------------
# Optional but recommended
# --------------------------------------------------
android.enable_androidx = True
android.gradle_dependencies = androidx.core:core:1.12.0

[graphics]
width = 360
height = 740

[network]
