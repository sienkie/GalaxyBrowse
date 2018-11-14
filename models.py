from abc import ABCMeta, abstractmethod
from constants import *
from shutil import copyfile
from utils import *
import argparse
import json
import os


class GalaxyBrowseScript(metaclass=ABCMeta):

    def __init__(self, args):
        """
        Args:
            args: sys.argv alike list for individual script parsers
        """
        self.args = args

    @abstractmethod
    def run(self):
        """
        Parse arguments and run script.
        """


class JBrowsePrepare(GalaxyBrowseScript):

    def __init__(self, args):
        super().__init__(args)
        self.files = []
        self.filetype = None
        self.visualization = None
        self.options = {}
        self.output = None
        self.index_dict = {}

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--input', nargs=2, action='append', help='Input datasets/files from Galaxy.')
        parser.add_argument('--input_index', nargs=2, action='append', help='Tabix index for input datasets/files.')
        parser.add_argument('--filetype', nargs=1, help='File type {either flat, wiggle or variant}')
        parser.add_argument('--output', nargs=1, help='Path to output dataset/file in Galaxy.')
        parser.add_argument('--option', nargs=2, action='append', help='Custom configuration options.')
        parser.add_argument('--options_file', nargs='?', help='Tab delimited file with configuration options.')
        args = parser.parse_args(self.args)

        if args.input:
            for dataset in args.input:
                self.files.append((dataset[0], dataset[1]))  # (path, name)
        else:
            raise AttributeError('Select at least one dataset!')
            # this should not happen due to specifications in wrapper file

        filetype = args.filetype[0].split(' ')
        if len(filetype) == 2:
            self.filetype, self.visualization = filetype[0], filetype[1]
        else:
            self.filetype = filetype[0]

        self.output = args.output[0]

        if self.filetype == 'variant':
            if args.input_index:
                for dataset in args.input_index:
                    self.index_dict[dataset[0]] = dataset[1]  # path of vcf : path of tbi
            if set([x[0] for x in self.files]) | set(list(self.index_dict.keys())) != set([x[0] for x in self.files]):
                raise AttributeError('Select tabix index file for every dataset!')
                # this should not happen due to specifications in wrapper file

        # configuration options have priority
        if args.option:
            for opt in args.option:
                if opt[0]:
                    if opt[0] not in self.options.keys():
                        formatted_opt = opt[1]
                        for key, value in mapped_chars.items():
                            # Unsanitize default element_identifiers sanitization by Galaxy
                            formatted_opt = formatted_opt.replace(value, key)
                        self.options[opt[0]] = formatted_opt
                    else:
                        print('WARNING: Some configuration options were omitted due to being repeated.')

        # configuration options file
        if args.options_file:
            with open(args.options_file, 'r') as f:
                lines = [line.split('\n')[0].split('\t') for line in f.readlines() if line]
                if any([len(x) > 2 or len(x) < 1 for x in lines]):
                    raise GalaxyBrowseParseError
                for line in lines:
                    opt = line[0]
                    val = line[1] if len(line) == 2 else ""
                    if opt not in self.options.keys():
                        self.options[opt] = val
                    else:
                        print('WARNING: Some configuration options were omitted due to being repeated.')

        supported = get_supported_data(self.filetype)
        if len(set(list(self.options.keys())) - set(supported)) != 0:
            print('WARNING: Some configuration options are not recognized.',
                  'Please refer to "Advanced configuration options" section below.')
            # TODO: Add to documentation:
            # TODO: uploading might not be successful, consider double-checking spelling and editing
            # TODO: trackList.json or tracks.conf files for more advanced configuration

        self.__prepare_with_options()

    def __prepare_with_options(self):
        with open(self.output, 'w') as out:
            data = {'files': []}
            number_of_files = len(self.files)
            # default configuration options
            default = get_default_data(self.filetype)

            for (fpath, fname) in self.files:
                file_data = {'file_path': fpath, 'file_type': self.filetype, 'data': self.options.copy()}

                if self.filetype == 'flat':
                    if 'trackLabel' not in self.options.keys() or 'trackLabel' in self.options.keys() \
                            and number_of_files != 1:
                        file_data['data']['trackLabel'] = ' '.join(fname.split('.')[:-1])

                elif self.filetype == 'wiggle':
                    if 'storeClass' in self.options.keys() and self.options['storeClass'] != default['storeClass']:
                        print("WARNING: Overwriting 'storeClass' of wiggle files is not recommended.")
                    if 'label' not in self.options.keys() or 'label' in self.options.keys() and number_of_files != 1:
                        file_data['data']['label'] = ' '.join(fname.split('.')[:-1])
                    assert self.visualization is not None
                    file_data['data']['type'] = "JBrowse/View/Track/Wiggle/" + self.visualization
                else:
                    if 'storeClass' in self.options.keys() and self.options['storeClass'] != default['storeClass']:
                        print("WARNING: Overwriting 'storeClass' of variant files is not recommended.")
                    if 'label' not in self.options.keys() or 'label' in self.options.keys() and number_of_files != 1:
                        file_data['data']['label'] = ' '.join(
                            fname.split('.')[:-2] if fname.split('.')[:-2] != [] else fname.split('.')[:-1])
                        file_data['data']['type'] = "JBrowse/View/Track/CanvasVariants"
                        file_data['data']['key'] = file_data['data']['label']
                        file_data['index_file_path'] = self.index_dict[fpath]

                for (key, val) in default.items():
                    # use option from default set if not specified otherwise in custom options
                    if key not in file_data['data'].keys():
                        file_data['data'][key] = val
                data['files'].append(file_data)
            json.dump(data, out)


class JBrowseAdd(GalaxyBrowseScript):

    def __init__(self, args):
        super().__init__(args)
        self.output_handle = None
        self.files = []
        self.jbrowse = None
        self.jbrowse_files = None
        self.curdir = None
        self.copy = False

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--input', nargs=1, action='append', help='Input JSON files from Galaxy.')
        parser.add_argument('--output', nargs=1, help='Verbose output.')
        parser.add_argument('--jbrowse', nargs=1, help='Path to main JBrowse directory.')
        parser.add_argument('--copy_files', required=False,
                            help="Copy files from Galaxy into JBrowse 'files' directory.")
        args = parser.parse_args(self.args)

        if args.copy_files:
            self.copy = True

        self.output_handle = open(args.output[0], "w")
        for file in args.input:
            with open(file[0], 'r') as f:
                data = json.load(f)
                try:
                    assert 'files' in data.keys()
                    for x in data['files']:
                        assert all(key in x.keys() for key in ["file_path", "file_type", "data"])
                except AssertionError:
                    raise ValueError("Incorrect structure of JSON file.")

            self.files += data['files']

        self.jbrowse = args.jbrowse[0]
        self.curdir = os.getcwd()

        if not self.jbrowse or not os.path.exists(self.jbrowse) or not os.path.exists(
                os.path.join(self.jbrowse, 'bin')):
            raise ValueError('Incorrect path to JBrowse directory.')
        elif not os.path.exists(os.path.join(self.jbrowse, 'data')):
            raise ValueError('JBrowse instance not ready for file uploading. '
                             'Add reference sequence to your browser before running script.')

        # TODO make sure access is preserved when galaxy and jbrowse are on different servers
        # if not os.access(self.jbrowse, os.W_OK):
        #     raise OSError('Jbrowse directory is not writable. Please set up appropriate privileges for Galaxy user')

        self.__set_up_file_structure()

        self.output_handle.write("#Changing working directory to main JBrowse directory.\n")
        os.chdir(self.jbrowse)

        for file in self.files:
            self.__upload_file(file)

        os.chdir(self.curdir)
        self.output_handle.close()

    def __set_up_file_structure(self):
        self.jbrowse_files = os.path.join(self.jbrowse, 'files')
        if not os.path.exists(self.jbrowse_files):
            line = "#Creating directory for "
            line += "symlinks" if not self.copy else "files"
            self.output_handle.write(line + ": " + self.jbrowse_files + ".\n")
            os.makedirs(self.jbrowse_files)

        files = [file["file_path"] for file in self.files]
        files += [file["index_file_path"] for file in self.files if 'index_file_path' in file.keys()]

        if not self.copy:
            self.output_handle.write("#Creating symlinks.\n")
            for file in files:
                if not os.path.exists(file):
                    raise FileNotFoundError("File: " + file + " does not exist!")
                try:
                    os.symlink(file, os.path.join(self.jbrowse_files, os.path.split(file)[-1]))
                except FileExistsError:
                    self.output_handle.write("Symlink for " + file + " already exists!\n")
        else:
            self.output_handle.write("#Copying files.\n")
            for file in files:
                if not os.path.exists(os.path.join(self.jbrowse_files, os.path.split(file)[-1])):
                    try:
                        copyfile(file, os.path.join(self.jbrowse_files, os.path.split(file)[-1]))
                    except FileNotFoundError:
                        self.output_handle.write("File: " + file + " does not exist!\n")
                else:
                    self.output_handle.write("File: " + file + " already exists in JBrowse 'files' directory!\n")

    def __upload_file(self, data):
        dataset = os.path.join('files', os.path.split(data["file_path"])[-1])
        self.output_handle.write("#Uploading " + dataset + ".\n")

        if data["file_type"] == "flat":
            repeats = check_track_labels(data['data']['trackLabel'], os.path.join('data', 'trackList.json'))
            if repeats > 0:
                new_name = data['data']['trackLabel'] + ' (' + str(repeats + 1) + ')'
                data['data']['trackLabel'] = new_name
                self.output_handle.write(
                    'Renamed ' + data['data']['trackLabel'] + ' to ' + new_name + ' due to track label duplications.')

            upload_command = ["bin/flatfile-to-json.pl", "--bed", dataset]
            json_config = {}
            json_style = {}
            for (key, val) in data["data"].items():
                if key in flatfile_config:
                    json_config[key] = val
                elif key in flatfile_style:
                    json_style[key] = val
                else:
                    upload_command += ["--" + key, val]
            if json_config:
                upload_command += ["--config", json.dumps(json_config)]
            if json_style:
                upload_command += ["--clientConfig", json.dumps(json_style)]
            for line in run_command(upload_command):
                self.output_handle.write(line.decode("utf-8"))

        elif data["file_type"] == "wiggle":
            repeats = check_track_labels(data['data']['label'], os.path.join('data', 'trackList.json'))
            if repeats > 0:
                data['data']['label'] = data['data']['label'] + ' (' + str(repeats + 1) + ')'

            file_data = {'urlTemplate': os.path.join('..', dataset)}
            json_style = {}
            for (key, val) in data["data"].items():
                if key in wiggle_style:
                    json_style[key] = val
                else:
                    file_data[key] = val
            if json_style:
                file_data['style'] = json_style

            with open(os.path.join('data', 'trackList.json'), 'r') as trackfile:
                trackdata = json.load(trackfile)

            trackdata["tracks"].append(file_data)
            with open(os.path.join('data', 'trackList.json'), 'w') as trackfile:
                json.dump(trackdata, trackfile)

        elif data["file_type"] == "variant":
            repeats = check_track_labels(data['data']['label'], os.path.join('data', 'trackList.json'))
            if repeats > 0:
                data['data']['label'] = data['data']['label'] + ' (' + str(repeats + 1) + ')'
                data['data']['key'] = data['data']['key'] + ' (' + str(repeats + 1) + ')'

            index_dataset = os.path.join('files', os.path.split(data["index_file_path"])[-1])
            file_data = {'urlTemplate': os.path.join('..', dataset),
                         'tbiUrlTemplate': os.path.join('..', index_dataset)}
            json_style = {}
            for (key, val) in data["data"].items():
                if key in variant_style:
                    json_style[key] = val
                else:
                    file_data[key] = val
            if json_style:
                file_data['style'] = json_style

            with open(os.path.join('data', 'trackList.json'), 'r') as trackfile:
                trackdata = json.load(trackfile)

            trackdata["tracks"].append(file_data)
            with open(os.path.join('data', 'trackList.json'), 'w') as trackfile:
                json.dump(trackdata, trackfile)

        else:
            self.output_handle.write(
                "File type " + data["file_type"] + " not supported! File " + dataset + " is omitted.\n")
            # this should not happen due to specifications in wrapper file


class JBrowseRemove(GalaxyBrowseScript):

    def __init__(self, args):
        super().__init__(args)
        self.output_handle = None
        self.files = []
        self.jbrowse = None
        self.labels = []
        self.curdir = None
        self.delete = False

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--input', nargs=1, action='append', help='Input JSON files from Galaxy.')
        parser.add_argument('--output', nargs=1, help='Verbose output.')
        parser.add_argument('--jbrowse', nargs=1, help='Path to main JBrowse directory.')
        parser.add_argument('--label', nargs=1, action='append', help='Label of track from JBrowse.')
        parser.add_argument('--delete', required=False,
                            help='Delete track data in addition to removing the track configuration.')
        args = parser.parse_args(self.args)

        if args.delete:
            self.delete = True

        if args.input:
            for file in args.input:
                self.files.append(file)

        if args.label:
            for label in args.label:
                self.labels.append(label[0])

        if not self.files and not self.labels:
            raise AttributeError('Select at least one JSON file or enter a track label.')

        self.jbrowse = args.jbrowse[0]
        self.curdir = os.getcwd()

        if not self.jbrowse or not os.path.exists(self.jbrowse) or not os.path.exists(
                os.path.join(self.jbrowse, 'bin')):
            raise ValueError('Incorrect path to JBrowse directory.')
        elif not os.path.exists(os.path.join(self.jbrowse, 'data')):
            raise ValueError('JBrowse instance not ready for file uploading. '
                             'Add reference sequence to your browser before running script.')

        self.output_handle = open(args.output[0], "w")
        for file in self.files:
            with open(file[0], 'r') as f:
                data = json.load(f)
                try:
                    assert 'files' in data.keys()
                    for file_json in data['files']:
                        assert "data" in file_json.keys()
                        assert any(key in file_json["data"].keys() for key in ["trackLabel", "label", "key"])
                        for x in ["trackLabel", "label", "key"]:
                            if x in file_json['data'].keys():
                                label = file_json['data'][x]
                                self.labels.append(label)
                                break

                except AssertionError:
                    raise ValueError("Incorrect structure of JSON file.")

        self.output_handle.write("#Changing working directory to main JBrowse directory.\n")
        os.chdir(self.jbrowse)

        for label in self.labels:
            self.__remove_track(label, delete=self.delete)

        os.chdir(self.curdir)
        self.output_handle.close()

    def __remove_track(self, label, delete=False):
        self.output_handle.write('#Removing track with label: ' + label + '.\n')
        upload_command = ['bin/remove-track.pl', '--trackLabel', label]
        if delete:
            upload_command.append('--delete')
        for line in run_command(upload_command):
            self.output_handle.write(line.decode("utf-8"))
