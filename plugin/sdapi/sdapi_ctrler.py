import base64
import re
import io
import json
import datetime
import pynvml
import subprocess
import socket
import psutil

from PIL import Image, PngImagePlugin

from .sdapi_model import WebUIApi, WebUIApiResult, HiResUpscaler, b64_bytes


class sdapi_ctrler_actions():

    def __init__(self) -> None:
        pass

    def open_json_file_as_base(self, name: str, dict_to_base: dict = {}):

        base = {}

        with open('./plugin/sdapi/'+name, 'r') as file:
            base = json.load(file)

        if bool(dict_to_base):
            for key in base:
                if key in dict_to_base:
                    base[key] = dict_to_base[key]

        return base

    def write_json_file_with_base(self, name: str, base_to_json: dict = {}):

        with open('./plugin/sdapi/'+name, 'w') as file:
            json.dump(base_to_json, file)

    def curse_trans_to_params(self, text: str) -> dict:

        patterns_dict = {
            'prompt': [r"(.*?)($|\n)"],
            'negative_prompt': [
                r"Negative prompt:(.*?)($|\n)", r"-ngt(.*?)($|\n)"],

            'steps': [
                r"Steps:(.*?)(,|$|\n)", r"-step(.*?)(,|$|\n)"],
            'sampler_name': [
                r"Sampler:(.*?)(,|$|\n)", r"-sampler(.*?)(,|$|\n)"],
            'n_iter': [
                r"-cnt(.*?)(,|$|\n)"],
            'cfg_scale': [
                r"CFG scale:(.*?)(,|$|\n)", r"-cfg(.*?)(,|$|\n)"],
            'seed': [
                r"Seed:(.*?)(,|$|\n)", r"-seed(.*?)(,|$|\n)"],
            'width': [
                r"Size:(.*?)(,|$|\n)", r"-size(.*?)(,|$|\n)"],
            'height': [
                r"Size:(.*?)(,|$|\n)", r"-size(.*?)(,|$|\n)"],
            'denoising_strength': [
                r"Denoising strength:(.*?)(,|$|\n)", r"-ds(.*?)(,|$|\n)"],
            'enable_hr': [
                r"-hr(.*?)(,|$|\n)"],
            'hr_scale': [
                r"Hires upscale:(.*?)(,|$|\n)", r"-upscale(.*?)(,|$|\n)"],
            'hr_upscaler': [
                r"Hires upscaler:(.*?)(,|$|\n)", r"-upscaler(.*?)(,|$|\n)"],
            'hr_second_pass_steps': [
                r"Hires steps:(.*?)(,|$|\n)", r"-hrsteps(.*?)(,|$|\n)"],

            'sd_model_checkpoint': [
                r"Model:(.*?)(,|$|\n)", r"-model(.*?)(,|$|\n)"],
            'CLIP_stop_at_last_layers': [
                r"Clip skip:(.*?)(,|$|\n)", r"-clip(.*?)(,|$|\n)"],
            'eta_noise_seed_delta': [
                r"ENSD:(.*?)(,|$|\n)", r"-ensd(.*?)(,|$|\n)"],
        }

        params = {
            'override_settings': {}
        }

        # 预处理

        text = text.replace('\n', '')

        for patterns_name, patterns in patterns_dict.items():

            if patterns_name == 'prompt':
                pass
            else:
                for pattern in patterns:
                    try:
                        item_proc1 = re.search(
                            pattern=pattern, string=text).group()
                        text = text.replace(item_proc1, '\n'+item_proc1)
                    except:
                        continue

        # 匹配

        bool_group = [
            'enable_hr'
        ]

        int_group = [
            'steps',
            'seed',
            'hr_second_pass_steps',
            'eta_noise_seed_delta',
            'CLIP_stop_at_last_layers',
            'n_iter'
        ]

        float_group = [
            'cfg_scale',
            'denoising_strength',
            'hr_scale'
        ]

        override_settings_group = [
            'sd_model_checkpoint',
            'CLIP_stop_at_last_layers',
            'eta_noise_seed_delta'
        ]

        for patterns_name, patterns in patterns_dict.items():

            for pattern in patterns:
                try:
                    item_proc1 = re.search(
                        pattern=pattern, string=text).group(1).strip()
                    if not bool(item_proc1):
                        continue
                except:
                    continue

                # 数据类型转换
                try:
                    if patterns_name in int_group:
                        item_proc2 = int(item_proc1)

                    elif patterns_name in float_group:
                        item_proc2 = round(float(item_proc1), 2)

                    elif patterns_name in bool_group:
                        item_proc2 = bool(int(item_proc1))

                    elif patterns_name == 'width':
                        item_proc2 = int(item_proc1.strip().split('x')[0])

                    elif patterns_name == 'height':
                        item_proc2 = int(item_proc1.strip().split('x')[1])

                    else:
                        item_proc2 = item_proc1

                except:
                    continue

                # 分组
                if patterns_name in override_settings_group:
                    params['override_settings'][patterns_name] = item_proc2

                else:
                    params[patterns_name] = item_proc2

        return params

    def curse_trans_to_params_for_extra(self, text: str) -> dict:

        patterns_dict = {
            'gfpgan_visibility': [
                r"-gfp(.*?)(,|$|\n)"],

            'codeformer_visibility': [
                r"-codeformer(.*?)(,|$|\n)"],

            'codeformer_weight': [
                r"-codeformerw(.*?)(,|$|\n)"],

            'upscaling_resize': [
                r"-resize(.*?)(,|$|\n)"],

            'upscaling_crop': [
                r"-crop(.*?)(,|$|\n)"],

            'upscaling_resize_w': [
                r"-tosize(.*?)(,|$|\n)"],

            'upscaling_resize_h': [
                r"-tosize(.*?)(,|$|\n)"],

            'upscaler_1': [
                r"-upscaler1(.*?)(,|$|\n)"],

            'upscaler_2': [
                r"-upscaler2(.*?)(,|$|\n)"],

            'extras_upscaler_2_visibility': [
                r"-upscaler2w(.*?)(,|$|\n)"],
        }

        params = {}

        # 预处理

        text = text.replace('\n', '')

        for patterns_name, patterns in patterns_dict.items():

            if patterns_name == 'prompt':
                pass
            else:
                for pattern in patterns:
                    try:
                        item_proc1 = re.search(
                            pattern=pattern, string=text).group()
                        text = text.replace(item_proc1, '\n'+item_proc1)
                    except:
                        continue

        # 匹配

        bool_group = [
            'upscaling_crop'
        ]

        int_group = []

        float_group = [
            'gfpgan_visibility',
            'codeformer_visibility',
            'codeformer_weight',
            'upscaling_resize',
            'extras_upscaler_2_visibility'
        ]

        for patterns_name, patterns in patterns_dict.items():

            for pattern in patterns:
                try:
                    item_proc1 = re.search(
                        pattern=pattern, string=text).group(1).strip()
                    if not bool(item_proc1):
                        continue
                except:
                    continue

                # 数据类型转换
                try:
                    if patterns_name in int_group:
                        item_proc2 = int(item_proc1)

                    elif patterns_name in float_group:
                        item_proc2 = round(float(item_proc1), 2)

                    elif patterns_name in bool_group:
                        item_proc2 = bool(int(item_proc1))

                    elif patterns_name == 'upscaling_resize_w':
                        item_proc2 = int(item_proc1.strip().split('x')[0])

                    elif patterns_name == 'upscaling_resize_h':
                        item_proc2 = int(item_proc1.strip().split('x')[1])

                    else:
                        item_proc2 = item_proc1

                except:
                    continue

                params[patterns_name] = item_proc2

        return params

    def save_pil_imgs(self, imgs: list, info: dict):
        path = list()

        for i in range(len(imgs)):

            # 加入图片参数
            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", str(info['infotexts'][i]))

            # 定义开始日期时间戳
            start_date = datetime.datetime(2023, 3, 12)

            # 获取当前日期时间戳
            now_date = datetime.datetime.now()

            # 计算时间差并转换为秒数
            time_difference = now_date - start_date
            timestamp = int(time_difference.total_seconds())

            imgs[i].save(
                'sdoutput/' + str(timestamp) + str(i) + '.png',
                pnginfo=pnginfo
            )

            path.append(
                ('sdoutput\\' + str(timestamp) + str(i) + '.png')
            )

        return path


class sdapi_ctrler():

    def __init__(self) -> None:
        self.sdpath = r'D:\stable-diffusion-webui\sd-inuse'
        self.sdp = self.sd_start()
        self.sd_wait('online')

        self.sdapi = WebUIApi()
        self.actions = sdapi_ctrler_actions()
        self.queue_count = 0

    def sd_start(self):
        # 运行webui-user.bat文件
        return subprocess.Popen(
            [self.sdpath + r'\launcher-bot.bat'])

    def sd_stop(self):
        global sdp

        # port 方法退出SD
        port = 7860

        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                pid = conn.pid
                print(pid)
                # 根据PID停止进程
                process = psutil.Process(pid)
                process.kill()

        # terminate 方法退出子线程
        sdp.terminate()

        # 等待子进程退出
        while sdp.poll() is None:
            pass

        # 获取子进程的退出状态
        return sdp.returncode

    def sd_ping(self):
        host = '127.0.0.1'
        port = 7860
        timeout = 5

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        result = sock.connect_ex((host, port))

        sock.close()

        if result == 0:
            return ("online")
        else:
            return ("offline")

    def sd_wait(self, status: str):

        response = self.sd_ping()

        while response != status:

            response = self.sd_ping()

    def get_queue(self) -> str:

        # 初始化pynvml
        pynvml.nvmlInit()

        mainGpuHandle = pynvml.nvmlDeviceGetHandleByIndex(0)

        # 获取当前显存使用情况
        mainGpuinfo = pynvml.nvmlDeviceGetMemoryInfo(mainGpuHandle)
        mainGpuUsage = mainGpuinfo.used / mainGpuinfo.total * 100

        # 获取GPU温度
        mainGpuTemp = pynvml.nvmlDeviceGetTemperature(
            mainGpuHandle, pynvml.NVML_TEMPERATURE_GPU)

        # 清理pynvml环境
        pynvml.nvmlShutdown()

        progress = self.sdapi.get_progress()

        if progress['state']['job_count'] != 0:
            workstr = "Working"
        else:
            self.queue_count = 0
            workstr = "Idle"

        return (
            "队列：%s, %d task(s)\n"
            "显卡：%.2f%%, %.1f°C\n"
            "任务剩时：%.2f s\n"
            "任务进度：%.2f%%, %d/%d"
            % (
                workstr, self.queue_count,
                mainGpuUsage, mainGpuTemp,
                progress['eta_relative'],
                progress['progress'] * 100,
                progress['state']['sampling_step'],
                progress['state']['sampling_steps'],
            )
        )

    def curse_to_img(self, curse: str = '', imgs: list = []):

        params = {}
        params = self.actions.curse_trans_to_params(curse)

        if bool(imgs):
            base_file = 'sd_img2img.json'
        else:
            base_file = 'sd_txt2img.json'

        base_params = {}
        base_params = self.actions.open_json_file_as_base(base_file, params)

        res: WebUIApiResult = None
        if bool(imgs):
            base_params['images'] = imgs
            res = self.sdapi.img2img(base_params)
        else:
            res = self.sdapi.txt2img(base_params)

        return self.actions.save_pil_imgs(res.images, res.info)

    def curse_to_file(self, curse: str = '', file_name: str = ''):

        params = self.actions.curse_trans_to_params(curse)

        base_params = {}
        base_params = self.actions.open_json_file_as_base(file_name, params)

        self.actions.write_json_file_with_base(file_name, base_params)
        if ('override_settings' in params) and bool(params['override_settings']):
            self.opr_options(params['override_settings'])

        res_params = []
        res_params = list(base_params.items())+list(self.opr_options().items())

        return [str(i) for i in res_params]

    def curse_to_file_for_extra(self, curse: str = ''):

        params = self.actions.curse_trans_to_params_for_extra(curse)

        base_params = {}
        base_params = self.actions.open_json_file_as_base(
            'sd_extra.json', params)

        self.actions.write_json_file_with_base('sd_extra.json', base_params)

        res_params = []
        res_params = list(base_params.items())

        return [str(i) for i in res_params]

    def imgs_to_extra(self, curse: str = '', img: list = []):

        params = {}
        params = self.actions.curse_trans_to_params_for_extra(curse)
        params["image"] = img[0]

        base_file = 'sd_extra.json'
        base_params = self.actions.open_json_file_as_base(base_file, params)

        res = self.sdapi.extra_single_image(base_params)

        img_add_params = {
            'infotexts': [
                base_params
            ]
        }

        return self.actions.save_pil_imgs(res.images, img_add_params)

    def get_pnginfo(self, img):

        if 'parameters' in img.info:
            return img.info['parameters']
        else:
            return 'None'

    def get_tagger(self, img):

        params = {
            "image": img
        }

        base_file = 'sd_tagger.json'
        base_params = self.actions.open_json_file_as_base(base_file, params)

        res_dict: dict = self.sdapi.tagger_image(base_params)

        general: float = round(res_dict['general']*100.0000, 2)
        sensitive: float = round(res_dict['sensitive']*100.0000, 2)
        questionable: float = round(res_dict['questionable']*100.0000, 2)
        explicit: float = round(res_dict['explicit']*100.0000, 2)

        del res_dict['general']
        del res_dict['sensitive']
        del res_dict['questionable']
        del res_dict['explicit']

        curse = [word for word in res_dict.keys()]

        return general, sensitive, questionable, explicit, curse

    def unload_tagger_model(self):
        self.sdapi.unload_tagger_models()

    def opr_options(self, settings: dict = None):
        if settings:
            self.sdapi.set_options(settings)
            return None

        else:
            base_options = {
                "sd_model_checkpoint": "",
                "sd_vae": "",
                "CLIP_stop_at_last_layers": "",
                "eta_noise_seed_delta": ""
            }

            options = self.sdapi.get_options()

            for key in base_options:
                base_options[key] = options[key]

            return base_options

    def reload_model(self):
        self.unload_tagger_model()
        self.sdapi.unload_checkpoint()
        self.sdapi.reload_checkpoint()

    def r_tagger_models(self):
        return self.sdapi.get_tagger_models()

    def w_tagger_settings(self, modelname: str = None, threshold: float = None):
        models_name_list = self.sdapi.get_tagger_models()

        base_params: dict = {}
        if bool(modelname):
            base_params['model'] = self.sdapi.util_find_similar_str(
                models_name_list, modelname)

        if bool(threshold):
            base_params['threshold'] = threshold

        base_params = self.actions.open_json_file_as_base(
            'sd_extra.json', base_params)

        self.actions.write_json_file_with_base(
            'sd_extra.json', base_params)

        return base_params

    def r_sampler(self):
        return self.sdapi.util_get_sampler_names()

    def w_sampler(self, dest_file: str, sampler_name: str) -> str:

        samplers_name_list = self.sdapi.util_get_sampler_names()

        dest_sampler = self.sdapi.util_find_similar_str(
            samplers_name_list, sampler_name)

        base_params = self.actions.open_json_file_as_base(
            dest_file, {'sampler_name': dest_sampler})

        self.actions.write_json_file_with_base(
            dest_file, base_params)

        return dest_sampler

    def r_upscaler(self):
        return self.sdapi.util_get_upscaler_names()

    def w_upscaler(self, is_upscaler2: bool = False, upscaler_name: str = 'None'):

        upcalers_name_list = self.sdapi.util_get_upscaler_names()

        dest_upscaler = self.sdapi.util_find_similar_str(
            upcalers_name_list, upscaler_name)

        base_params = {}

        if not is_upscaler2:
            base_params = self.actions.open_json_file_as_base(
                'sd_extra.json', {'upscaler_1': dest_upscaler})
        else:
            base_params = self.actions.open_json_file_as_base(
                'sd_extra.json', {'upscaler_2': dest_upscaler})

        if not bool(base_params):
            return None

        self.actions.write_json_file_with_base(
            'sd_extra.json', base_params)

        return dest_upscaler

    def r_hiresupscaler(self):
        return self.sdapi.uitl_get_hires_upscaler_names()

    def w_hiresupsacler(self, dest_file: str, upscaler_name: str):

        upcalers_name_list = self.sdapi.uitl_get_hires_upscaler_names()

        dest_upscaler = self.sdapi.util_find_similar_str(
            upcalers_name_list, upscaler_name)

        base_params = self.actions.open_json_file_as_base(
            dest_file, {'hr_upscaler': dest_upscaler})

        self.actions.write_json_file_with_base(
            dest_file, base_params)

        return dest_upscaler

    def r_models(self) -> list:
        self.sdapi.refresh_checkpoints()
        return self.sdapi.util_get_model_names()

    def w_models(self, modelname: str) -> str:
        return self.sdapi.util_set_model(modelname)

    def r_vae(self):
        try:
            return self.sdapi.util_get_vae_names()
        except:
            return []

    def w_vae(self, vaename: str):

        return self.sdapi.util_set_vae(vaename)
