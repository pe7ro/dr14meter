import pathlib
import sys

import dr14meter.dr14_main as dr14


file = pathlib.Path('data/sample_audio_with_metadata.wav')

def run():
    sys.argv = [str(x) for x in sys.argv]
    print(f' ### {sys.argv} ### ')
    ret = dr14.main()
    print(ret)


sys.argv = [__file__, 'data']
run()


sys.argv = [__file__, '--skip', 'data']
run()


sys.argv = [__file__, '-f', file]
run()


sys.argv = [__file__, '-1', '-f', file]
run()


x = pathlib.Path('data', 'filelist')
x.write_text(str(file))
sys.argv = [__file__, '--files_list', x]
run()


sys.argv = [__file__, '--hist', file]
run()


sys.argv = [__file__, '--lev_hist', file]
run()


sys.argv = [__file__, '--spectrogram', file]
run()


sys.argv = [__file__, '--plot_track', file]
run()


# sys.argv = [__file__, '--plot_track_dst', file]
# run()


sys.argv = [__file__, '--compress', 'soft', file]
run()


sys.argv = [__file__, '--dyn_vivacity', file]
run()


sys.argv = [__file__, '-v']
run()


sys.argv = [__file__, '-p', file.parent]
run()

