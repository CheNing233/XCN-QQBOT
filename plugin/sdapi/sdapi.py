import os
import io
import requests
from PIL import Image

from pycqbot_core.cqApi import cqBot, cqHttpApi
from pycqbot_core.object import Plugin, Message
from pycqbot_core.cqCode import *

from .sdapi_ctrler import sdapi_ctrler


class sdapi_cq_actions:

    def __init__(self, cqBot: cqBot, cqHttpApi: cqHttpApi, plugin_config) -> None:
        self.bot = cqBot
        self.cqapi = cqHttpApi
        self.plugincfg = plugin_config

    # 应答普通消息（不回复）
    def ans_normal_message(self, message: Message, messageStr: str):
        if message.type == "group":
            self.cqapi.send_group_msg(
                group_id=message.group_id,
                message=messageStr
            )
        else:
            self.cqapi.send_private_msg(
                user_id=message.user_id,
                message=messageStr
            )

    # 应答合并转发消息（不回复）
    def ans_forward_message(self, message: Message, messageStrList: list):
        if message.type == "group":
            self.cqapi.send_group_forward_msg(
                group_id=message.group_id,
                message=node_list(
                    name='小心海',
                    uin='3265595625',
                    message_list=messageStrList
                )
            )
        else:
            self.cqapi.send_private_forward_msg(
                user_id=message.user_id,
                message=node_list(
                    name='小心海',
                    uin='3265595625',
                    message_list=messageStrList
                )
            )

    # 应答一张本地表情（不回复）
    def ans_local_face(self, message: Message, faceName: str):

        imgcqcode = image(
            faceName,
            "file:///" + os.getcwd() + "\\facepack\\" + faceName
        )

        self.ans_normal_message(message, imgcqcode)

    # 递归搜索指定cqcode（进入回复）
    def search_cqcode(self, text: str = "", msgid: int = None, cqDictList_dest: list = list(), destCqcode: str = ""):

        if bool(msgid):
            text = self.cqapi.get_msg(msgid)
            cqDictList = strToCqCodeToDict((text['data']['message']))
        else:
            cqDictList = strToCqCodeToDict(text)

        cqDict_reply = None

        # 遍历所有Cqcode
        for cqDict in cqDictList:

            if cqDict['type'] == destCqcode:
                cqDictList_dest.append(cqDict)

            if cqDict['type'] == 'reply':
                cqDict_reply = cqDict

        if bool(cqDict_reply):
            return self.search_cqcode(
                text=None,
                msgid=int(cqDict_reply['data']['id']),
                cqDictList_dest=cqDictList_dest,
                destCqcode=destCqcode
            )

        else:

            return cqDictList_dest

    # cqcode到url导pil图片
    def cqcode_to_pil_img(self, cqcode) -> list:
        img = []
        urls = []

        if str(type(cqcode)) == '<class \'dict\'>':

            urls.append(cqcode['data']['url'])

            for url in urls:

                try:
                    res = requests.get(url=url)
                except:
                    res = None

        elif str(type(cqcode)) == '<class \'str\'>':

            temp = strToCqCodeToDict(str(cqcode))
            for dict in temp:
                urls.append(dict['data']['url'])

            for url in urls:

                try:
                    res = requests.get(url=url)
                except:
                    res = None

        if bool(res) and res.status_code == 200:
            img.append(Image.open(io.BytesIO(res.content)))

        return img

    # 根据file-id获取pil图片
    def get_group_img(self, message: Message, file_id) -> list:

        try:
            url = self.cqapi.get_group_file_url(
                group_id=message.group_id,
                file_id=file_id,
                busid=102
            )['data']['url']

            response = requests.get(url=url)
        except:
            return []

        return [Image.open(io.BytesIO(response.content))]


class sdapi(Plugin):

    ctrler = None
    actions = None

    def __init__(self, bot: cqBot, cqapi: cqHttpApi, plugin_config) -> None:
        super().__init__(bot, cqapi, plugin_config)

        self.ctrler = sdapi_ctrler()
        self.actions = sdapi_cq_actions(bot, cqapi, plugin_config)

        bot.command(self.sd, "sd", {
            "type": "all"
        }).command(self.sddraw, "sddraw", {
            "type": "all"
        }).command(self.sdextra, "sdextra", {
            "type": "all"
        }).command(self.sdinf, "sdinf", {
            "type": "all"
        }).command(self.sdtxt, "sdtxt", {
            "type": "all"
        }).command(self.sdimg, "sdimg", {
            "type": "all"
        }).command(self.sdext, "sdext", {
            "type": "all"
        }).command(self.sdextupscaler, "sdextupscaler", {
            "type": "all"
        }).command(self.sdtagger, "sdtagger", {
            "type": "all"
        }).command(self.sdfrev, "sdfrev", {
            "type": "all"
        }).command(self.sdmodel, "sdmodel", {
            "type": "all"
        }).command(self.sdvae, "sdvae", {
            "type": "all"
        }).command(self.sdsampler, "sdsampler", {
            "type": "all"
        }).command(self.sdupscaler, "sdupscaler", {
            "type": "all"
        })

    def sd(self, commandData: list, message: Message):
        inf = self.ctrler.get_queue()

        self.actions.ans_normal_message(message, inf)

    def sddraw(self, commandData: list, message: Message):

        self.ctrler.queue_count += 1

        self.actions.ans_normal_message(
            message, '♥ 收到喵，现在有%d个任务喵~' % (self.ctrler.queue_count))

        try:
            self.ctrler.unload_tagger_model()
        except:
            pass

        cqcodeDictList_img = []
        cqcodeDictList_img = self.actions.search_cqcode(
            text=' '.join(commandData), cqDictList_dest=[], destCqcode='image')

        pil_imgs = []
        if bool(cqcodeDictList_img):
            pil_imgs = self.actions.cqcode_to_pil_img(cqcodeDictList_img[0])

        commandData = commandDataRemoveAllCqcode(commandData)
        curse = ' '.join(commandData)

        try:
            paths = self.ctrler.curse_to_img(curse, pil_imgs)
        except:
            self.actions.ans_normal_message(message, '喵~ 出错了！')
            self.ctrler.queue_count -= 1
            return None

        self.ctrler.queue_count -= 1

        if self.ctrler.queue_count == 0:
            self.actions.ans_normal_message(message, "画完喵！")

        for key in paths:

            cqimgs = image("return.png", "file:///" + os.getcwd() + "\\" + key)

            self.actions.ans_normal_message(message, cqimgs)

    def sdextra(self, commandData: list, message: Message):

        pil_imgs = []

        if commandData[0] == '-id':

            pil_imgs = self.actions.get_group_img(
                message=message, file_id=commandData[1])

            if not bool(pil_imgs):
                self.actions.ans_normal_message(
                    message=message, messageStr="喵，get不到喵")
                return None

        else:
            cqcodeDictList_img = []
            cqcodeDictList_img = self.actions.search_cqcode(
                text=' '.join(commandData), cqDictList_dest=[], destCqcode='image')

            pil_imgs = self.actions.cqcode_to_pil_img(
                cqcodeDictList_img[0])

        try:

            paths = self.ctrler.imgs_to_extra(' '.join(commandData), pil_imgs)

        except:

            self.actions.ans_normal_message(message, '喵~ 出错了！')
            return None

        for key in paths:

            cqimgs = image("return.png", "file:///" + os.getcwd() + "\\" + key)

            self.actions.ans_normal_message(message, cqimgs)

    def sdinf(self, commandData: list, message: Message):

        pil_imgs = []
        file_id = None
        en_tagger = False

        for i in range(len(commandData)):
            if commandData[i] == '-id' and i+1 in range(len(commandData)):
                file_id = commandData[i+1]
            if commandData[i] == '-tagger':
                en_tagger = True

        if file_id:

            pil_imgs = self.actions.get_group_img(
                message=message, file_id=file_id)

            if not bool(pil_imgs):
                self.actions.ans_normal_message(
                    message=message, messageStr="喵，get不到喵")
                return None

        else:
            cqcodeDictList_img = []
            cqcodeDictList_img = self.actions.search_cqcode(
                text=' '.join(commandData), cqDictList_dest=[], destCqcode='image')

            pil_imgs = self.actions.cqcode_to_pil_img(
                cqcodeDictList_img[0])

        try:
            res_pnginfo = self.ctrler.get_pnginfo(pil_imgs[0])
        except:
            res_pnginfo = 'None'

        curse = ['None']
        if en_tagger:

            try:
                general, sensitive, questionable, explicit, curse = self.ctrler.get_tagger(
                    pil_imgs[0])

            except:
                general, sensitive, questionable, explicit = None

            if bool(general) and bool(sensitive) and bool(questionable) and bool(explicit):
                self.actions.ans_normal_message(
                    message=message,
                    messageStr="涩涩鉴定\n"
                    "无害(general)：%.2f%%\n"
                    "H(sensitive)：%.2f%%\n"
                    "涩(questionable)：%.2f%%\n"
                    "大咩(explicit)：%.2f%%"
                    % (
                        general, sensitive, questionable, explicit
                    )
                )
                if explicit > 10 or questionable > 50:
                    self.actions.ans_local_face(
                        message=message, faceName='h.jpg')

        self.actions.ans_forward_message(
            message,
            [
                "提取的infotext为：",
                str(res_pnginfo),
                "Tagger反推结果为：",
                ', '.join(curse)
            ]
        )

    def sdtagger(self, commandData: list, message: Message):

        for i in range(len(commandData)):
            if commandData[i] == '-model':

                if i+1 in range(len(commandData)):
                    model = commandData[i+1]
                else:
                    model = None

            if commandData[i] == '-thres' and i+1 in range(len(commandData)):
                threshold = round(float(commandData[i+1]), 2)

        self.ctrler.w_tagger_settings(model, threshold)

    def sdtxt(self, commandData: list, message: Message):

        commandData = commandDataRemoveAllCqcode(commandData)
        curse = ' '.join(commandData)

        res = self.ctrler.curse_to_file(curse, 'sd_txt2img.json')

        self.actions.ans_forward_message(
            message=message, messageStrList=(['文生图参数']+res))

    def sdimg(self, commandData: list, message: Message):

        commandData = commandDataRemoveAllCqcode(commandData)
        curse = ' '.join(commandData)

        res = self.ctrler.curse_to_file(curse, 'sd_img2img.json')

        self.actions.ans_forward_message(
            message=message, messageStrList=(['图生图参数']+res))

    def sdext(self, commandData: list, message: Message):

        commandData = commandDataRemoveAllCqcode(commandData)
        curse = ' '.join(commandData)

        res = self.ctrler.curse_to_file_for_extra(curse)

        self.actions.ans_forward_message(
            message=message, messageStrList=(['图像放大参数']+res))

    def sdextupscaler(self, commandData: list, message: Message):
        if bool(commandData):

            upscaler = self.ctrler.w_upscaler(
                is_upscaler2=False, upscaler_name=' '.join(commandData))

            if bool(upscaler):
                self.actions.ans_normal_message(
                    message=message, messageStr='♥ 图像放大方法已改为：'+upscaler
                )
            else:
                self.actions.ans_normal_message(
                    message=message, messageStr='切换失败喵`(*>﹏<*)′'
                )

        else:

            upscaler_list = self.ctrler.r_upscaler()

            self.actions.ans_forward_message(
                message=message,
                messageStrList=[
                    "♥ 当前可用放大方法为："]+upscaler_list
            )

    def sdsampler(self, commandData: list, message: Message):

        if bool(commandData):

            if commandData[0] == '-txt':
                del commandData[0]
                sampler = self.ctrler.w_sampler(
                    'sd_txt2img.json', ' '.join(commandData))
            elif commandData[0] == '-img':
                del commandData[0]
                sampler = self.ctrler.w_sampler(
                    'sd_img2img.json', ' '.join(commandData))
            else:
                self.actions.ans_normal_message(
                    message=message, messageStr='喵，看不懂捏`(*>﹏<*)′'
                )
                return None

            if bool(sampler):
                self.actions.ans_normal_message(
                    message=message, messageStr='♥ 采样器已改为：'+sampler
                )
            else:
                self.actions.ans_normal_message(
                    message=message, messageStr='切换失败喵`(*>﹏<*)′'
                )

        else:

            sampler_list = self.ctrler.r_sampler()

            self.actions.ans_forward_message(
                message=message,
                messageStrList=[
                    "♥ 当前可用采样器为："]+sampler_list
            )

    def sdupscaler(self, commandData: list, message: Message):
        if bool(commandData):

            if commandData[0] == '-txt':
                del commandData[0]
                upscaler = self.ctrler.w_hiresupsacler(
                    'sd_txt2img.json', ' '.join(commandData))
            elif commandData[0] == '-img':
                del commandData[0]
                upscaler = self.ctrler.w_hiresupsacler(
                    'sd_img2img.json', ' '.join(commandData))
            else:
                self.actions.ans_normal_message(
                    message=message, messageStr='喵，看不懂捏`(*>﹏<*)′'
                )
                return None

            if bool(upscaler):
                self.actions.ans_normal_message(
                    message=message, messageStr='♥ 高清修复方法已改为：'+upscaler
                )
            else:
                self.actions.ans_normal_message(
                    message=message, messageStr='切换失败喵`(*>﹏<*)′'
                )

        else:

            upscaler_list = self.ctrler.r_hiresupscaler()

            self.actions.ans_forward_message(
                message=message,
                messageStrList=[
                    "♥ 当前可用高清修复方法为："]+upscaler_list
            )

    def sdmodel(self, commandData: list, message: Message):
        if not bool(commandData):
            models_list = self.ctrler.r_models()

            self.actions.ans_forward_message(
                message=message,
                messageStrList=[
                    "♥ 当前可用模型为："]+models_list
            )

        else:
            name = ' '.join(commandData)
            res = self.ctrler.w_models(name)
            if bool(res):
                self.actions.ans_normal_message(
                    message=message, messageStr='♥ 模型已改为：'+res
                )
            else:
                self.actions.ans_normal_message(
                    message=message, messageStr='切换失败喵`(*>﹏<*)′'
                )

    def sdvae(self, commandData: list, message: Message):

        if not bool(commandData):
            vaes_list = self.ctrler.r_vae()

            self.actions.ans_forward_message(
                message=message,
                messageStrList=["♥ 当前可用VAE为："]+vaes_list
            )

        else:
            name = ' '.join(commandData)
            res = self.ctrler.w_vae(name)
            if bool(res):
                self.actions.ans_normal_message(
                    message=message, messageStr='♥ VAE已改为：'+res
                )
            else:
                self.actions.ans_normal_message(
                    message=message, messageStr='切换失败喵`(*>﹏<*)′'
                )

    def sdfrev(self, commandData: list, message: Message):
        self.ctrler.reload_model()
        self.actions.ans_local_face(
            message, 'reloaded.gif'
        )

    def notice_group_upload(self, message_dict):
        """
        群文件上传
        """
        self.cqapi.send_group_msg(
            group_id=message_dict['group_id'],
            message=message_dict['file']['id']
        )

        self.cqapi.send_group_msg(
            group_id=message_dict['group_id'],
            message="文件ID喵 ( •̀ ω •́ )y"
        )
