from flask_assets import Environment, Bundle

def bundle_css_files(app):
   # CSSファイルのバンドル（圧縮・結合）
   assets = Environment(app)
   css_bundle = Bundle('css/*.css', filters='cssmin', output='gen/bundled.css')
   assets.register('css_all', css_bundle)
   # 環境に登録したバンドルでビルド（登録前のオブジェクトではパス解決ができない）
   with app.app_context():
       assets['css_all'].build()