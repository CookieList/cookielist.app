from flask import redirect, request, send_file, url_for, session
from flask_classful import FlaskView, route
from functools import cache
import orjson
from cookielist.environment import env
from cookielist.assets import asset


@cache
def generate_web_manifest():
    return {
        "short_name": env.string("WEBAPP_NAME"),
        "name": f"{env.string('WEBAPP_NAME')} - Better statistics for AniList.",
        "icons": [
            {
                "src": url_for(
                    "static", filename="images/icons/windows/SmallTile.scale-100.png"
                ),
                "sizes": "71x71",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/SmallTile.scale-125.png"
                ),
                "sizes": "89x89",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/SmallTile.scale-150.png"
                ),
                "sizes": "107x107",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/SmallTile.scale-200.png"
                ),
                "sizes": "142x142",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/SmallTile.scale-400.png"
                ),
                "sizes": "284x284",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square150x150Logo.scale-100.png",
                ),
                "sizes": "150x150",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square150x150Logo.scale-125.png",
                ),
                "sizes": "188x188",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square150x150Logo.scale-150.png",
                ),
                "sizes": "225x225",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square150x150Logo.scale-200.png",
                ),
                "sizes": "300x300",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square150x150Logo.scale-400.png",
                ),
                "sizes": "600x600",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Wide310x150Logo.scale-100.png",
                ),
                "sizes": "310x150",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Wide310x150Logo.scale-125.png",
                ),
                "sizes": "388x188",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Wide310x150Logo.scale-150.png",
                ),
                "sizes": "465x225",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Wide310x150Logo.scale-200.png",
                ),
                "sizes": "620x300",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Wide310x150Logo.scale-400.png",
                ),
                "sizes": "1240x600",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/LargeTile.scale-100.png"
                ),
                "sizes": "310x310",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/LargeTile.scale-125.png"
                ),
                "sizes": "388x388",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/LargeTile.scale-150.png"
                ),
                "sizes": "465x465",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/LargeTile.scale-200.png"
                ),
                "sizes": "620x620",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/LargeTile.scale-400.png"
                ),
                "sizes": "1240x1240",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.scale-100.png",
                ),
                "sizes": "44x44",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.scale-125.png",
                ),
                "sizes": "55x55",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.scale-150.png",
                ),
                "sizes": "66x66",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.scale-200.png",
                ),
                "sizes": "88x88",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.scale-400.png",
                ),
                "sizes": "176x176",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/StoreLogo.scale-100.png"
                ),
                "sizes": "50x50",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/StoreLogo.scale-125.png"
                ),
                "sizes": "63x63",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/StoreLogo.scale-150.png"
                ),
                "sizes": "75x75",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/StoreLogo.scale-200.png"
                ),
                "sizes": "100x100",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/StoreLogo.scale-400.png"
                ),
                "sizes": "200x200",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/SplashScreen.scale-100.png"
                ),
                "sizes": "620x300",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/SplashScreen.scale-125.png"
                ),
                "sizes": "775x375",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/SplashScreen.scale-150.png"
                ),
                "sizes": "930x450",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/SplashScreen.scale-200.png"
                ),
                "sizes": "1240x600",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static", filename="images/icons/windows/SplashScreen.scale-400.png"
                ),
                "sizes": "2480x1200",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-16.png",
                ),
                "sizes": "16x16",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-20.png",
                ),
                "sizes": "20x20",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-24.png",
                ),
                "sizes": "24x24",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-30.png",
                ),
                "sizes": "30x30",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-32.png",
                ),
                "sizes": "32x32",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-36.png",
                ),
                "sizes": "36x36",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-40.png",
                ),
                "sizes": "40x40",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-44.png",
                ),
                "sizes": "44x44",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-48.png",
                ),
                "sizes": "48x48",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-60.png",
                ),
                "sizes": "60x60",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-64.png",
                ),
                "sizes": "64x64",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-72.png",
                ),
                "sizes": "72x72",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-80.png",
                ),
                "sizes": "80x80",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-96.png",
                ),
                "sizes": "96x96",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.targetsize-256.png",
                ),
                "sizes": "256x256",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-16.png",
                ),
                "sizes": "16x16",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-20.png",
                ),
                "sizes": "20x20",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-24.png",
                ),
                "sizes": "24x24",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-30.png",
                ),
                "sizes": "30x30",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-32.png",
                ),
                "sizes": "32x32",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-36.png",
                ),
                "sizes": "36x36",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-40.png",
                ),
                "sizes": "40x40",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-44.png",
                ),
                "sizes": "44x44",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-48.png",
                ),
                "sizes": "48x48",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-60.png",
                ),
                "sizes": "60x60",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-64.png",
                ),
                "sizes": "64x64",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-72.png",
                ),
                "sizes": "72x72",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-80.png",
                ),
                "sizes": "80x80",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-96.png",
                ),
                "sizes": "96x96",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-unplated_targetsize-256.png",
                ),
                "sizes": "256x256",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-16.png",
                ),
                "sizes": "16x16",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-20.png",
                ),
                "sizes": "20x20",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-24.png",
                ),
                "sizes": "24x24",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-30.png",
                ),
                "sizes": "30x30",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-32.png",
                ),
                "sizes": "32x32",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-36.png",
                ),
                "sizes": "36x36",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-40.png",
                ),
                "sizes": "40x40",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-44.png",
                ),
                "sizes": "44x44",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-48.png",
                ),
                "sizes": "48x48",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-60.png",
                ),
                "sizes": "60x60",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-64.png",
                ),
                "sizes": "64x64",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-72.png",
                ),
                "sizes": "72x72",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-80.png",
                ),
                "sizes": "80x80",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-96.png",
                ),
                "sizes": "96x96",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/windows/Square44x44Logo.altform-lightunplated_targetsize-256.png",
                ),
                "sizes": "256x256",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/android/android-launchericon-512-512.png",
                ),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/android/android-launchericon-192-192.png",
                ),
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/android/android-launchericon-144-144.png",
                ),
                "sizes": "144x144",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/android/android-launchericon-96-96.png",
                ),
                "sizes": "96x96",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/android/android-launchericon-72-72.png",
                ),
                "sizes": "72x72",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(
                    "static",
                    filename="images/icons/android/android-launchericon-48-48.png",
                ),
                "sizes": "48x48",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/16.png"),
                "sizes": "16x16",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/20.png"),
                "sizes": "20x20",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/29.png"),
                "sizes": "29x29",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/32.png"),
                "sizes": "32x32",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/40.png"),
                "sizes": "40x40",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/50.png"),
                "sizes": "50x50",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/57.png"),
                "sizes": "57x57",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/58.png"),
                "sizes": "58x58",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/60.png"),
                "sizes": "60x60",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/64.png"),
                "sizes": "64x64",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/72.png"),
                "sizes": "72x72",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/76.png"),
                "sizes": "76x76",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/80.png"),
                "sizes": "80x80",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/87.png"),
                "sizes": "87x87",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/100.png"),
                "sizes": "100x100",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/114.png"),
                "sizes": "114x114",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/120.png"),
                "sizes": "120x120",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/128.png"),
                "sizes": "128x128",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/144.png"),
                "sizes": "144x144",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/152.png"),
                "sizes": "152x152",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/167.png"),
                "sizes": "167x167",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/180.png"),
                "sizes": "180x180",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/192.png"),
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/256.png"),
                "sizes": "256x256",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/512.png"),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for("static", filename="images/icons/ios/1024.png"),
                "sizes": "1024x1024",
                "type": "image/png",
                "purpose": "any",
            },
        ],
        "id": "/?source=pwa",
        "start_url": "/?source=pwa",
        "background_color": None,
        "dir": "ltr",
        "lang": "en",
        "edge_side_panel": {"preferred_width": 480},
        "orientation": "portrait",
        "display_override": [
            "window-controls-overlay",
            "standalone",
            "minimal-ui",
            "browser",
        ],
        "theme_color": None,
        "display": "standalone",
        "scope": "/",
        "shortcuts": [],
        "description": f"{env.string('WEBAPP_NAME')}: Simplifying media counts on AniList. Unlike AniList's individual title count, {env.string('WEBAPP_NAME')} tallies by series. Watching multiple seasons, movies, and OVAs of a series only counts as one entry.",
        "screenshots": [
            {
                "src": url_for("static", filename="images/screenshots/narrow-1.png"),
                "type": "image/png",
                "sizes": "1284x2778",
                "form_factor": "narrow",
            },
            {
                "src": url_for("static", filename="images/screenshots/narrow-2.png"),
                "type": "image/png",
                "sizes": "1284x2778",
                "form_factor": "narrow",
            },
            {
                "src": url_for("static", filename="images/screenshots/narrow-3.png"),
                "type": "image/png",
                "sizes": "1284x2778",
                "form_factor": "narrow",
            },
            {
                "src": url_for("static", filename="images/screenshots/narrow-4.png"),
                "type": "image/png",
                "sizes": "1284x2778",
                "form_factor": "narrow",
            },
            {
                "src": url_for("static", filename="images/screenshots/narrow-5.png"),
                "type": "image/png",
                "sizes": "1284x2778",
                "form_factor": "narrow",
            },
            {
                "src": url_for("static", filename="images/screenshots/wide-1.png"),
                "type": "image/png",
                "sizes": "1920x913",
                "form_factor": "wide",
            },
            {
                "src": url_for("static", filename="images/screenshots/wide-2.png"),
                "type": "image/png",
                "sizes": "1920x913",
                "form_factor": "wide",
            },
            {
                "src": url_for("static", filename="images/screenshots/wide-3.png"),
                "type": "image/png",
                "sizes": "1920x913",
                "form_factor": "wide",
            },
            {
                "src": url_for("static", filename="images/screenshots/wide-4.png"),
                "type": "image/png",
                "sizes": "1920x913",
                "form_factor": "wide",
            },
            {
                "src": url_for("static", filename="images/screenshots/wide-5.png"),
                "type": "image/png",
                "sizes": "1920x913",
                "form_factor": "wide",
            },
            {
                "src": url_for("static", filename="images/screenshots/wide-5.png"),
                "type": "image/png",
                "sizes": "1920x913",
                "form_factor": "wide",
            },
            {
                "src": url_for("static", filename="images/screenshots/wide-5.png"),
                "type": "image/png",
                "sizes": "1920x913",
                "form_factor": "wide",
            },
        ],
    }


class AboutView(FlaskView):
    route_base = "/"
    default_methods = ["GET"]

    @route("/")
    def index(self):
        return redirect(
            url_for(
                "UserPageView:user_page",
                id=str(session.get("id", env.string("ANILIST_DEV_ID"))),
            )
        )

    @route("/robots.txt")
    def robots_txt(self):
        return "\n".join(
            [
                "User-agent: *",
                "Disallow: /_/",
                "Disallow: /api/",
            ]
        )

    @route("/favicon.ico")
    def favicon_ico(self):
        return send_file(asset.path("favicon.ico"), max_age=24 * 60 * 60)

    @route("/manifest.webmanifest")
    def webmanifest(self):
        manifest = generate_web_manifest()

        theme = (
            request.cookies.get("theme")
            if request.cookies.get("theme") in {"light", "dark"}
            else "light"
        )
        theme = {
            "dark": "#252627",
            "light": "#e2e8f0",
        }[theme]
        manifest["background_color"] = theme
        manifest["theme_color"] = theme

        for history in orjson.loads(request.cookies.get("history", "{}")):
            manifest["shortcuts"].append(
                {
                    "name": f"{history['name']}'s CookieList",
                    "short_name": history["name"],
                    "description": f"View @{history['name']}'s CookieList page",
                    "url": f"/{history['id']}?source=pwa",
                }
            )
        return manifest
