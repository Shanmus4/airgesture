from gesture_mvp_ui import GestureMVPApp
from remi import start

if __name__ == '__main__':
    start(GestureMVPApp, address='0.0.0.0', port=8081, debug=True, update_interval=0.05) 