[buildozer]
log_level = 2

[app]
title = WaterReminder
package.name = waterreminder
package.domain = org.example

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,ttf,mp3

version = 0.1

requirements = python3,kivy,pyjnius

orientation = portrait
fullscreen = 1

android.api = 34
android.minapi = 21

# ❌ android.build_tools_version REMOVED

android.sdk_path = /home/runner/android-sdk
android.ndk_path = /home/runner/android-sdk/ndk/25.2.9519653

android.permissions = POST_NOTIFICATIONS,WAKE_LOCK
android.allow_backup = True
android.icon.filename = assets/icon.png

android.enable_androidx = True
android.gradle_dependencies = androidx.core:core:1.12.0

[graphics]
width = 360
height = 740

[network]
