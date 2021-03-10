#
# for help: plots.py [-h] 
#

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy import signal
import argparse
import os
import copy

np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)

mpl.rcParams['figure.titlesize'] = 'small'
# mpl.rcParams['ytick.minor.visible'] = True
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['font.size'] = 10
mpl.rcParams['legend.fontsize'] = 'large'


def calculate_fft(sig, fs, N=None,
                  remove_dc=True, norm_amplitude=False,
                  window='hahn',
                  decim_factor=1):
    # sig = copy.deepcopy(sig)

    if decim_factor > 1:
        sig = sig[::decim_factor]
        fs /= decim_factor

    if remove_dc: sig -= np.mean(sig)

    if N is None:
        N = sig.size
    else:
        sig = sig[:N]

    if window == 'hann':
        win = np.hanning(N)
        beta = np.sum(win) / N
        sig = sig * win / beta
    else:
        # rectangular window
        pass

    ampl = np.abs(np.fft.fft(sig, n=N))[:N // 2]
    freqs = np.fft.fftfreq(N, 1 / fs)[:N // 2]

    if norm_amplitude:
        ampl /= N
        ampl[1:] *= 2

    return np.column_stack([freqs, ampl])


def plot_fft_xyz(x, y, z,
                 label='',
                 save_fig=False,
                 show_fig=False,
                 y_scale='linear',
                 label_peaks=10,
                 Y_min=None, Y_max=None,
                 F_min=None, F_max=None):
    i_start = 0
    i_stop = x[:, 0].size
    if F_min: i_start = np.squeeze(np.where(x[:, 0] < F_min))[-1]
    if F_max:
        if F_max >= x[-1, 0]:
            i_stop = x[:, 0].size - 1
        else:
            i_stop = np.squeeze(np.where(x[:, 0] >= F_max))[0]
    x = x[i_start:i_stop]
    y = y[i_start:i_stop]
    z = z[i_start:i_stop]

    f, ax = plt.subplots(3, 1, figsize=(10, 6), sharex=True, sharey=True)  # , gridspec_kw={'width_ratios':[5, 2.5]})

    colors = ['#EF2800', '#0bB623', '#1231D3']
    labels = ['x', 'y', 'z']
    for i, axis_spectrum in enumerate([x, y, z]):
        ax[i].plot(axis_spectrum[:, 0], axis_spectrum[:, 1],
                   c=colors[i], lw=1, label=labels[i])

        if label_peaks > 0:
            ind, ampl = signal.find_peaks(axis_spectrum[:, 1],
                                          distance=2)
            peaks = axis_spectrum[ind][np.argsort(axis_spectrum[ind, 1])][-label_peaks:]
            ax[i].plot(peaks[:, 0], peaks[:, 1], 'k.', markersize=1)

            print(labels[i])
            print(peaks[::-1])

            # for p in peaks:
            #    #ax.annotate('(%s, %s)' % xy, xy=xy, textcoords='data')
            #    ax[i,0].annotate("{:.2f}, {:.2f}".format(p[0],p[1]),
            #                xy = (p[0],p[1]),
            #                textcoords='data',
            #                rotation=90,
            #                horizontalalignment = 'center',
            #                verticalalignment = 'bottom',
            #                fontsize=8)

    ax[1].set_ylabel('Ampl, $m/s^2$')
    ax[2].set_xlabel('Freq, Hz')

    for a in ax.flatten():
        a.grid(linestyle='-', lw=.3, which='minor')
        a.grid(linestyle='-', lw=.5, which='major')
        a.set_axisbelow(True)
        a.set_yscale(y_scale)
        a.minorticks_on()
        a.locator_params(axis="x", tight=True, nbins=10)
        # a.locator_params(axis="y", tight=True, numticks =10)
        a.legend(loc='upper right')

    if Y_max is None:
        Y_max = np.max([np.max(x[:, 1]), np.max(y[:, 1]), np.max(z[:, 1])])
        if y_scale == 'log': Y_max *= 2
        if y_scale == 'linear': Y_max *= 1.2
    if Y_min is None:
        Y_min = np.min([np.median(x[:, 1]), np.median(y[:, 1]), np.median(z[:, 1])])
        Y_min *= 0.01
    # plt.ylim([Ymin, Ymax])

    ax[0].set_title('Fourier spectra for 3 axes\n' + label)
    plt.tight_layout()
    plt.subplots_adjust(hspace=0)
    if save_fig:
        plt.savefig(f'{label}-fft.png')

    if show_fig:
        plt.show(block=False)


def parse_accel_raw(f_name):
    description = 'No description'
    frequency = 1
    units = 'n/a'
    data = []
    ts = 0

    c = 1
    for line in open(f_name):
        if "Description:" in line:
            description = line.split(':')[1][1:]
        if "Sampling frequency:" in line:
            frequency = float(line.split(' ')[2])
        if "Units:" in line:
            units = line.split(' ')[1]
        if "TS:" in line:
            ts = float(line.split(':')[1].split(' ')[1])
        if "Data:" in line:
            print(c)
            print('now load the data')
            break
        c += 1
    data = np.loadtxt(f_name, skiprows=c)

    return ({
        'description': description,
        'frequency': frequency,
        'ts': ts,
        'units': units,
        'data': data
    })


def parse_accel_fft(f_name):
    description = 'No description'
    lines = 1
    units = 'n/a'
    frequency = 1
    start_freq = 0
    end_freq = 1
    data = []

    c = 1
    for line in open(f_name):

        if "Description:" in line:
            description = line.split(':')[1][1:]
        if "Sampling frequency:" in line:
            frequency = float(line.split(' ')[2])
        if "Units:" in line:
            units = line.split(' ')[1]
        if "Lines:" in line:
            lines = int(line.split(':')[1].split(' ')[1])
        if "Starting frequency:" in line:
            start_freq = float(line.split(':')[1].split(' ')[1])
        if "Ending frequency:" in line:
            end_freq = float(line.split(':')[1].split(' ')[1])
        if "Data:" in line:
            print(c)
            print('now load the data')
            break
        c += 1
    data = np.loadtxt(f_name, skiprows=c)
    freqs = np.linspace(start_freq, end_freq, lines)

    return (
        {
            'description': description,
            'frequency': frequency,
            'units': units,
            'freqs': freqs,
            'spectrum_x': np.column_stack([freqs, data[:, 0]]),
            'spectrum_y': np.column_stack([freqs, data[:, 1]]),
            'spectrum_z': np.column_stack([freqs, data[:, 2]])
        }
    )


def plot_accel_raw(raw, save_fig=False, show_fig=False, subtitle='', align_y_scale=True):
    axes_labels = ['x', 'y', 'z']

    number_of_axes = raw['data'].shape[1]
    ts = np.arange(0, raw['data'].shape[0] / raw['frequency'], 1 / raw['frequency'])

    inset_ratio = 0.05
    inset_len = int(ts.size * inset_ratio)
    main_wf_end = ts.size - inset_len

    colors = ['#EF2800', '#0bB623', '#1231D3', 'c', 'm', 'y', 'k']
    labels = ['x', 'y', 'z']

    fig, ax = plt.subplots(number_of_axes, 3, figsize=(8, 5), dpi=100, gridspec_kw={'width_ratios': [.5, 5, 2.5]})

    for i in range(number_of_axes):
        n, bins, patches = ax[i, 0].hist(raw['data'][:, i], color=colors[i], bins=50, orientation="horizontal",
                                         alpha=0.5)

        # ax[i,0].set_xlim(ax[i,0].get_xlim()[::-1])

        # add small shift
        # mi, ma = ax[i,0].get_xlim()
        # ax[i,0].set_xlim(( ma, mi - np.abs(ma-mi)*0.5) )

        ax[i, 0].set_ylabel('{:s}, ${:s}$\nMean:{:7.3f}\nStd:{:7.3f}'.format(
            axes_labels[i],
            raw['units'][:-1],
            np.mean(raw['data'][:, i]),
            np.std(raw['data'][:, i])
        ),
            rotation=0,
            horizontalalignment='right',
            verticalalignment='center')

        ax[i, 1].plot(ts[:main_wf_end], raw['data'][:main_wf_end, i], color=colors[i], lw=.5, label=labels[i])
        ax[i, 1].legend(loc='upper right')
        ax[i, 2].plot(ts[-inset_len:], raw['data'][-inset_len:, i], color=colors[i], lw=.5)

    if align_y_scale:
        delta_y_axis = 0
        for a in ax.flatten():
            min_y, max_y = a.yaxis.get_data_interval()
            delta_y = max_y - min_y
            if delta_y > delta_y_axis:
                delta_y_axis = delta_y

        for a in ax.flatten():
            min_y, max_y = a.yaxis.get_data_interval()
            delta_y = max_y - min_y
            center_y = min_y + 0.5 * delta_y
            a.set_ylim(center_y - delta_y_axis / 2, center_y + delta_y_axis / 2)

    for i in (0, 1, 2):

        ax[i, 2].grid("true", alpha=0.5, linestyle=':')
        ax[i, 2].set_axisbelow('True')
        for a in (ax[i, 1], ax[i, 2]):
            a.margins(0, None)

    ax[0, 1].set_title(raw['description'] + ' ' + f"{subtitle}")
    ax[-1, 1].set_xlabel('time, s')

    # Join axes for zooming
    ax[0, 1].get_shared_x_axes().join(ax[0, 1], ax[1, 1])
    ax[0, 1].get_shared_x_axes().join(ax[0, 1], ax[2, 1])

    ax[0, 1].get_shared_y_axes().join(ax[0, 1], ax[0, 0])
    ax[1, 1].get_shared_y_axes().join(ax[1, 1], ax[1, 0])
    ax[2, 1].get_shared_y_axes().join(ax[2, 1], ax[2, 0])

    ax[0, 2].get_shared_x_axes().join(ax[0, 2], ax[1, 2])
    ax[1, 2].get_shared_x_axes().join(ax[0, 2], ax[2, 2])

    fig.align_ylabels((ax[0, 0], ax[1, 0], ax[2, 0]))
    plt.tight_layout()
    for i in (0, 1):
        for j in (0, 1, 2):
            ax[i, j].set_xticklabels([])
    for i in (0, 1, 2):
        ax[i, 1].set_yticklabels([])
        ax[i, 2].set_yticklabels([])
    ax[2, 0].set_xticklabels([])

    plt.subplots_adjust(wspace=0.0, hspace=0.05)

    if save_fig:
        plt.savefig(f'{subtitle}-waveform.png', dpi=300)

    if show_fig:
        plt.show(block=False)


# def parse_accel_fft()
# def parse_accel_distribution()
# def parse_temperature()
# def parse_battery()

if __name__ == "__main__":
    print(os.getcwd())
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="input accel_raw file", required=True)
    # parser.add_argument("-f", "--freq", type=float, help="data frequency", default=100000)
    parser.add_argument("-s", "--savefig", action='store_true', help='save figure in png file', default=False)
    parser.add_argument("-p", "--print", action='store_true', help='show figures on the screen', default=False)
    parser.add_argument("-n", "--name", type=str, help="Custom name of measurement", default='', required=False)
    parser.add_argument("-fmin", "--fmin", type=int, help="Min frequency on spectra plots", default=None,
                        required=False)
    parser.add_argument("-fmax", "--fmax", type=int, help="Max frequency on spectra plots", default=None,
                        required=False)
    parser.add_argument("-ylog", "--ylog", action='store_true', help="Use log scale on spectra plots", default=False,
                        required=False)

    args = parser.parse_args()
    print(args)

    if args.name == '':  # Fill measurement name to show on plots
        args.name = os.path.split(args.input)[1]

    y_scale = 'linear'
    if args.ylog:
        y_scale = 'log'

    raw = parse_accel_raw(args.input)
    plot_accel_raw(raw, save_fig=args.savefig, subtitle=args.name, show_fig=args.print)

    fft_filename = args.input.replace('raw.log', 'fft.log')  # generate name of file with Fourier spectra from device

    if os.path.exists(fft_filename):
        fft_embed = parse_accel_fft(fft_filename)  # parse file spectra
        plot_fft_xyz(fft_embed['spectrum_x'],  # plot spectra
                     fft_embed['spectrum_y'],
                     fft_embed['spectrum_z'],
                     label=f'{args.name}-embed',
                     F_min=args.fmin, F_max=args.fmax,
                     y_scale=y_scale,
                     save_fig=args.savefig,
                     show_fig=args.print)
    else:
        print('Warning: accel_fft file not found')

    # calculate Fourier spectra
    spectrum_x = calculate_fft(raw['data'][:, 0], raw['frequency'], remove_dc=False, norm_amplitude=True, window='hann',
                               decim_factor=1)
    print(spectrum_x)
    spectrum_y = calculate_fft(raw['data'][:, 1], raw['frequency'], remove_dc=False, norm_amplitude=True, window='hann',
                               decim_factor=1)
    print(spectrum_y)
    spectrum_z = calculate_fft(raw['data'][:, 2], raw['frequency'], remove_dc=False, norm_amplitude=True, window='hann',
                               decim_factor=1)
    print(spectrum_z)

    # plot calculated Fourier spectra
    print('Calculated spectra peaks:')
    plot_fft_xyz(spectrum_x,
                 spectrum_y,
                 spectrum_z,
                 label=f'{args.name}-calculated',
                 F_min=args.fmin, F_max=args.fmax,
                 y_scale=y_scale,
                 save_fig=args.savefig,
                 show_fig=args.print)

    if args.print:
        plt.show()
