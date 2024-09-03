from util.gui import my_gui
from util.config import create_config

from new_folder import create_folders


# ======== 可更改的参量 BEGIN ========
# 以下是可更改的参量，可以根据需要进行修改，也可在图形化界面进行修改
# 执行顺序（可在这里调整脚本执行顺序）
execution_order = ['new_folder','capture','remove','stitch','detect','recut','pdf'] #别改这个

# remove.py 参数
remove_params = {
    'is_similar_threshold': 0.1,
    'is_colorful_threshold': 20,
    'is_colorful_grey': 20,
    'is_mostly_black_black_threshold': 0.6,
    'range': 10,
    'cut_right': 0.2,
}

# stitch.py 参数
stitch_params = {
    'cut_up': 0.5,
    'cut_bot': 0.1,
    'cut_right': 0.25,
    'test': False,
    'reco_limit':0.9
}

# capture.py 参数
capture_params = {
    'start':0,
    'segment_duration':20,
    'frame_interval':1,
    'score_threshold': 200,
    'light_threshold': 250,
    'search_area': 'bottom',
}
detect_params = {
    'manual': True,
    'single_line': True,
}
pdf_params = {
    'lines':6,
}



if __name__ == '__main__':
    create_config('config.ini', {
        'remove'    : remove_params,
        'stitch'    : stitch_params,
        'capture'   : capture_params,
        'detect'    : detect_params,
        'pdf'       : pdf_params,
    })

    main_gui = my_gui()     # 实例化自定义 gui
    main_gui.mainloop()

    if( main_gui.new_folder ):
        create_folders()
    if( main_gui.capture ):
        ...
    if( main_gui.remove ):
        ...
    if( main_gui.stitch ):
        ...
    if( main_gui.detect ):
        ...
    if( main_gui.recut ):
        ...
    if( main_gui.pdf ):
        ...

    print(main_gui.capture)