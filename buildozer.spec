[buildozer]
log_level = 2

[app]
title = WaterReminder
package.name = waterreminder
package.domain = org.example

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,ttf

version = 0.1

requirements = python3,kivy,pyjnius

orientation = portrait

fullscreen = 1

android.api = 33
android.minapi = 21

android.permissions = POST_NOTIFICATIONS,WAKE_LOCK

android.allow_backup = True

android.icon.filename = assets/icon.png

[graphics]
width = 360
height = 740

[network]
