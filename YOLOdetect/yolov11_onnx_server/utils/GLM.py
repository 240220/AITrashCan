import pyttsx3
import cv2
import base64
import zhipuai

def ask_GLM(image_cv):
    image = cv2.imencode('.jpg', image_cv)[1]
    img_base = str(base64.b64encode(image))[2:-1]
    zhipuai.api_key="7e9645e2131a497c9e04197a4e509893.Ef6MHlbsP75lcLeN"  # 填写您自己的APIKey
    response = zhipuai.model_api.sse_invoke(
        model="glm-4v-plus-0111",  # 填写需要调用的模型名称
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_base
                        }
                    },
                    {
                        "type": "text",
                        "text": "请问这里有哪些物体，分别是什么类别的垃圾"
                    }
                ]
            }
        ]
    )
    print(response)
    # res_txt = response.choices[0].message.content
    # return res_txt
    return "aaa"
def say_txt(txt):
    engine = pyttsx3.init()
    engine.say(txt)
    engine.runAndWait()
if __name__ == "__main__":
    img_path = "E:\gongchuang\mydata\images\WIN_20250305_16_53_26_Pro.jpg"
    image_cv = cv2.imread(img_path)
    res_txt = ask_GLM(image_cv)
    print(res_txt)
    say_txt(res_txt)

