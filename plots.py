#
# for help: plots.py [-h] 
#

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy import signal
import argparse
import os


# parser = argparse.ArgumentParser()
# parser.add_argument("-i", "--input", type=str, help="input accel_raw file", required=True)
# # parser.add_argument("-f", "--freq", type=float, help="data frequency", default=100000)
# parser.add_argument("-s", "--savefig", action='store_true', help='save figure in png file', default=False)
# parser.add_argument("-p", "--print", action='store_true', help='show figures on the screen', default=False)
# parser.add_argument("-n", "--name", type=str, help="Custom name of measurement", default='', required=False)
# parser.add_argument("-fmin", "--fmin", type=int, help="Min frequency on spectra plots", default=None, required=False)
# parser.add_argument("-fmax", "--fmax", type=int, help="Max frequency on spectra plots", default=None, required=False)
# parser.add_argument("-ylog", "--ylog", action='store_true', help="Use log scale on spectra plots", default=False,
#                     required=False)


class Plots:
    np.set_printoptions(precision=3)
    np.set_printoptions(suppress=True)
    mpl.rcParams['figure.titlesize'] = 'small'
    # mpl.rcParams['ytick.minor.visible'] = True
    mpl.rcParams['savefig.dpi'] = 300
    mpl.rcParams['font.size'] = 10
    mpl.rcParams['legend.fontsize'] = 'large'

    def __init__(self, arguments, boolraw):
        if boolraw:
            self.file_name = arguments.input
        else:
            self.file_name = arguments.input.replace('raw.log', 'fft.log')
        self.file_name = arguments.input
        self.args = arguments
        self.description = 'No description'
        self.lines = float
        self.units = 'n/a'
        self.frequency = float
        self.start_freq = float
        self.end_freq = float
        self.data = []
        self.ts = float
        self.ampl = None
        self.frequency = None
        self.colors = ['#EF2800', '#0bB623', '#1231D3', 'c', 'm', 'y', 'k']
        self.labels = ['x', 'y', 'z']
        self.inset_ratio = 0.05
        self.save_fig = arguments.savefig
        self.show_fig = arguments.print
        self.y_scale = str

    def parse_accel_fft(self):
        c = 1
        with open(self.file_name) as file:
            for line in file:
                if "Description:" in line:
                    self.description = line.split(':')[1][1:]
                if "Sampling frequency:" in line:
                    self.frequency = float(line.split(' ')[2])
                if "Units:" in line:
                    self.units = line.split(' ')[1]
                if "Lines:" in line:
                    self.lines = int(line.split(':')[1].split(' ')[1])
                if "Starting frequency:" in line:
                    self.start_freq = float(line.split(':')[1].split(' ')[1])
                if "Ending frequency:" in line:
                    self.end_freq = float(line.split(':')[1].split(' ')[1])
                if "Data:" in line:
                    print(c)
                    print('now load the data')
                    break
                c += 1
        self.data = np.loadtxt(self.file_name, skiprows=c)
        self.frequency = np.linspace(self.start_freq, self.end_freq, self.lines)
        return (
            {
                'description': self.description,
                'frequency': self.frequency,
                'units': self.units,
                'freqs': self.frequency,
                'spectrum_x': np.column_stack([self.frequency, self.data[:, 0]]),
                'spectrum_y': np.column_stack([self.frequency, self.data[:, 1]]),
                'spectrum_z': np.column_stack([self.frequency, self.data[:, 2]])
            }
        )

    def parse_accel_raw(self):
        c = 1
        for line in open(self.file_name):
            if "Description:" in line:
                self.description = line.split(':')[1][1:]
            if "Sampling frequency:" in line:
                self.frequency = float(line.split(' ')[2])
            if "Units:" in line:
                self.units = line.split(' ')[1]
            if "TS:" in line:
                self.ts = float(line.split(':')[1].split(' ')[1])
            if "Data:" in line:
                print(c)
                print('now load the data')
                break
            c += 1
        self.data = np.loadtxt(self.file_name, skiprows=c)
        return ({
            'description': self.description,
            'frequency': self.frequency,
            'ts': self.ts,
            'units': self.units,
            'data': self.data
        })

    def calculate_fft(self, sig, fs, N=None, remove_dc=True, norm_amplitude=False, window='hahn', decim_factor=1):
        # sig = copy.deepcopy(sig)
        if decim_factor > 1:
            sig = sig[::decim_factor]
            fs /= decim_factor
        if remove_dc:
            sig -= np.mean(sig)
        if not N:
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
        self.ampl = np.abs(np.fft.fft(sig, n=N))[:N // 2]
        self.frequency = np.fft.fftfreq(N, 1 / fs)[:N // 2]
        if norm_amplitude:
            self.ampl /= N
            self.ampl[1:] *= 2
        return np.column_stack([self.frequency, self.ampl])

    def plot_fft_xyz(self, x, y, z, label='', label_peaks=10,
                     y_min=None, y_max=None,
                     f_min=None, f_max=None):
        i_start = 0
        i_stop = x[:, 0].size
        if f_min:
            i_start = np.squeeze(np.where(x[:, 0] < f_min))[-1]
        if f_max:
            if f_max >= x[-1, 0]:
                i_stop = x[:, 0].size - 1
            else:
                i_stop = np.squeeze(np.where(x[:, 0] >= f_max))[0]
        x = x[i_start:i_stop]
        y = y[i_start:i_stop]
        z = z[i_start:i_stop]

        f, ax = plt.subplots(3, 1, figsize=(10, 6), sharex='all', sharey='all')

        for i, axis_spectrum in enumerate([x, y, z]):
            ax[i].plot(axis_spectrum[:, 0], axis_spectrum[:, 1],
                       c=self.colors[i], lw=1, label=self.labels[i])

            if label_peaks > 0:
                ind, ampl = signal.find_peaks(axis_spectrum[:, 1],
                                              distance=2)
                peaks = axis_spectrum[ind][np.argsort(axis_spectrum[ind, 1])][-label_peaks:]
                ax[i].plot(peaks[:, 0], peaks[:, 1], 'k.', markersize=1)

                print(self.labels[i])
                print(peaks[::-1])

        ax[1].set_ylabel('Ampl, $m/s^2$')
        ax[2].set_xlabel('Freq, Hz')

        for a in ax.flatten():
            a.grid(linestyle='-', lw=.3, which='minor')
            a.grid(linestyle='-', lw=.5, which='major')
            a.set_axisbelow(True)
            a.set_yscale(self.y_scale)
            a.minorticks_on()
            a.locator_params(axis="x", tight=True, nbins=10)
            # a.locator_params(axis="y", tight=True, numticks =10)
            a.legend(loc='upper right')

        if y_max is None:
            y_max = np.max([np.max(x[:, 1]), np.max(y[:, 1]), np.max(z[:, 1])])
            if self.y_scale == 'log':
                y_max *= 2
            if self.y_scale == 'linear':
                y_max *= 1.2
        if y_min is None:
            y_min = np.min([np.median(x[:, 1]), np.median(y[:, 1]), np.median(z[:, 1])])
            y_min *= 0.01
        # plt.ylim([Ymin, Ymax])

        # ax[0].set_title('Fourier spectra for 3 axes\n' + label)
        plt.tight_layout()
        plt.subplots_adjust(hspace=0)

        # if self.save_fig:
        return f
        # if self.save_fig:
        #    plt.savefig(f'{label}-fft.png')
        # if self.show_fig:
        #    plt.show(block=False)

    def plot_accel_raw(self, raw, subtitle='', align_y_scale=True):
        number_of_axes = raw['data'].shape[1]
        ts = np.arange(0, raw['data'].shape[0] / raw['frequency'], 1 / raw['frequency'])
        inset_len = int(ts.size * self.inset_ratio)
        main_wf_end = ts.size - inset_len
        fig, ax = plt.subplots(number_of_axes, 3, figsize=(8, 5), dpi=100, gridspec_kw={'width_ratios': [.5, 5, 2.5]})
        for i in range(number_of_axes):
            ax[i, 0].hist(raw['data'][:, i], color=self.colors[i], bins=50, orientation="horizontal",
                          alpha=0.5)
            ax[i, 0].set_ylabel('{:s}, ${:s}$\nMean:{:7.3f}\nStd:{:7.3f}'.format(
                self.labels[i],
                raw['units'][:-1],
                np.mean(raw['data'][:, i]),
                np.std(raw['data'][:, i])
            ),
                rotation=0,
                horizontalalignment='right',
                verticalalignment='center')

            ax[i, 1].plot(ts[:main_wf_end], raw['data'][:main_wf_end, i], color=self.colors[i], lw=.5,
                          label=self.labels[i])
            ax[i, 1].legend(loc='upper right')
            ax[i, 2].plot(ts[-inset_len:], raw['data'][-inset_len:, i], color=self.colors[i], lw=.5)

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

        for i in range(2):
            ax[i, 2].grid("true", alpha=0.5, linestyle=':')
            ax[i, 2].set_axisbelow('True')
            for a in (ax[i, 1], ax[i, 2]):
                a.margins(0, None)

        # ax[0, 1].set_title(raw['description'] + ' ' + f"{subtitle}")
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
        for i in range(1):
            for j in range(2):
                ax[i, j].set_xticklabels([])
        for i in range(2):
            ax[i, 1].set_yticklabels([])
            ax[i, 2].set_yticklabels([])
        ax[2, 0].set_xticklabels([])

        plt.subplots_adjust(wspace=0.0, hspace=0.05)

        # if self.save_fig:
        #    plt.savefig(f'{subtitle}-waveform.png', dpi=300)

        # if self.show_fig:
        #    plt.show(block=False)

        return fig

    def run(self, view):
        if self.args.name == '':  # Fill measurement name to show on plots
            self.args.name = os.path.split(self.args.input)[1]
        if self.args.ylog:
            self.y_scale = 'log'
        else:
            self.y_scale = 'linear'

        raw = self.parse_accel_raw()
        if view == 'raw':
            fig = self.plot_accel_raw(raw, subtitle=self.args.name)
            return fig
        elif view == 'fft_spectra':
            print("имя файла ", self.file_name)
            fft_embed = self.parse_accel_fft()
            fig = self.plot_fft_xyz(fft_embed['spectrum_x'],  # plot spectra
                                    fft_embed['spectrum_y'],
                                    fft_embed['spectrum_z'],
                                    label=f'{self.args.name}-embed',
                                    f_min=self.args.fmin, f_max=self.args.fmax, )
            return fig
        elif view == 'Fourier_spectra':
            print("имя файла ", self.file_name)
            # calculate Fourier spectra
            spectrum_x = self.calculate_fft(raw['data'][:, 0], raw['frequency'], remove_dc=False,
                                            norm_amplitude=True,
                                            window='hann',
                                            decim_factor=1)
            print(spectrum_x)
            spectrum_y = self.calculate_fft(raw['data'][:, 1], raw['frequency'], remove_dc=False,
                                            norm_amplitude=True,
                                            window='hann',
                                            decim_factor=1)
            print(spectrum_y)
            spectrum_z = self.calculate_fft(raw['data'][:, 2], raw['frequency'], remove_dc=False,
                                            norm_amplitude=True,
                                            window='hann',
                                            decim_factor=1)
            print(spectrum_z)

            # plot calculated Fourier spectra
            print('Calculated spectra peaks:')
            fig = self.plot_fft_xyz(spectrum_x,
                                    spectrum_y,
                                    spectrum_z,
                                    label=f'{self.args.name}-calculated',
                                    f_min=self.args.fmin, f_max=self.args.fmax, )
            return fig
        # if self.args.print:
        # plt.show()
        # return plt


if __name__ == "__main__":
    #  В комментах args для тестирования, чтобы вечно не использовать командную строку
    # args = parser.parse_args()
    args = argparse.Namespace(input='data//IIS3DWB//2021-03-08-19-05-51-accel_fft.log',
                              savefig=False,
                              print=True,
                              name='',
                              fmin=None,
                              fmax=None,
                              ylog=True)
    # plot = Plots(arguments=args, boolraw='true')
    plot = Plots(arguments=args, boolraw='true')
    # view = 'raw'
    # view = 'fft_spectra'
    view = 'Fourier_spectra'
    # plot.run(view).show()
    # fig = plot.run(view).show()
    fig = plot.run(view)
    print("type fig", type(fig))
    # plt.show()
