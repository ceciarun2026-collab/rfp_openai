"""
app.py - Frontend Streamlit para el Evaluador RFP con IA
Ejecutar con: streamlit run app.py
"""

import io
import os
import shutil
import tempfile
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# ── Variables de entorno ──────────────────────────────────────────────────────
load_dotenv()
os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="RFP Evaluator · Runbss",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>R</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

LOGO_B64 = "iVBORw0KGgoAAAANSUhEUgAAAQQAAACkCAYAAABxY1BQAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAC+oSURBVHhe7V0JgFxVla2tO0knZAECiCODYBhEVEQGRwZHFGQAmREcHQQdBvdBkTVJdzaSQDrdCVtYxBFFnXFURlxYBERlU3CURZBNloR9TQdoyNpdy59z7rvv/1fVtXb/6u50v3P7vXfPufe/X1X93qv/a/mV8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDwGKNIajtsuO59/za9r5DfE+5OqdaWyWibdhtMx8lEUvcQcmnhhbqNGCQ1EHIbV4E8VQg2B/l8z/1vvPy70x68PjARD4+tG3bMNxU/+9vjpueD4LB0MvlV0HeiTJNAE2GndGOLQWm+Ew91m2nAxSMb5P84MZV5IBEkfjujZdKP97nt630a9vDYqmDHdVNw0lv/LnPI9rv/cz4RdGJHPCpoOux0bWwhoF7CbVyFRvKDRHBNIUj85sa1j3/znNW390vAw2MrgB3PseN/33vMjJZU+nK4Rxul+bBTlJMy9KWFp06tiR1moLIRtjZee+EoqZOJ/8kWCt885PffvV1ED49RDB3G8eKa/T/z13iWvA6nCe9Qqamw0690Uto7Rz2cuFJTK+ZhBiobsbFIdzXNUkFZVKMKc0y5vS3Tev6+t176cxE9PEYhzIiNET/Z79jpmVTq9sIwLAZ2ulVbCCyPNJtlofmobMTGIt1GDMjrXQhMK6LwVCL5i2xQOPkfbv/2kybq4TF6kNI2NqSTye80ezHgxDKT0kzMkIvBp8aY5SiSobM45KIxN2QwEy/Xh/jUSJSHNapq+ZYHicSRLcnUE7878AvtkDw8RhU4TmPD1ft/+gScJnxXaewwN9ZMMOOZ2t4Joztc6+L8KCPSbaapiri0IhZzaU3VeL5xUsnkPROSmSPffeslL4nk4THCsGN2yLhyv09NxQD/Pwz+vVSKDXYCjf6FwNSV+zeOhi3vTSSDQ/e/7Zt3CfXwGEHEeMqQPBhDPdbFgBOG06f0sNsYfGqiK7elKJ9FjZro1jTOfJdbk1yHSy6Lw91tqDMebqO+aNasBt/kT08lknfe9cH/+BBkD48RRWwLAo4OTlB3yDCTJpwwERfjZNLiaqLDZ7HcGnNZQtN4zXyrKZdc5e421BkP82nwqTnbEJX2icfv5j8ddOIHJcnDY4QQy4KwaI8PcewfpHRIMBOHk0YcmSxhjUpKaPSpwWdRbjPkTwTl4lEDc/JNlBpjkWZrVuppbbjpx2jCxeBTY0w5Ib5olptaWubDgkTimnsP+sq+EvLwGAHEsiDsM20nfhx5qmGDAydGOGlkgii3MVaqRBp8nWQSlhg1xkIGM3GjO9ya6JEW1qJrjrsNNcYsF2MuS8QJ8YvyVaNJvuWJRDqRnAp+Q8/hHZO4rYfHcCOWBSGXSb1J3YYRTpCiSWMNPjXGLBcNvmiGsxaT3JDBTNzokUaIJ7o0httadJNtVBMx+424rVkZXblIsKJ8G1dNdGsmThG2w0tbNlxN6uEx3IhlQZiQTE9Xt26EE6Ro0liTuWFiljv5hKlVY4vK+MqtVqEPk294WFOrI98Yc7WEiuYU5Ufx0vwwLvkRx6nDRx748ElHwfXwGFbE9qJivTCDXicASMjF4FOTyaG8bL5qNGql+eU0GjXG3O0HnV+iiQ6fxXJrzGUJTePV8hOJpn2ew8OjEjgOh4yrDjj+mEI2d4XSsjA7MoPdeKa2N8DoDte6OD/KiHSbacAJJq3UGjd/EZfWVAO217rs7URVxMVjVcJtHFURF89UVimKi25AJR8EX3vXLZdcotKowqIzl74pl8/vGxQKby4UClNTqVRGQwOQy+b++9xzu19QKjj9jLnvbW1t/YjSAQiC4OUV3Z0NL4rtHQtOwBjYSekAIHZr1/Kz/6B0UJg3f9G0zZs375XJZN7W0tIyLZvtb0PPAfp+BY/DE5lMy+87ly3ZKr/lasffkFBtQQgHvO4p5NLCC3UbMSg7sdmqMKR8VAO21zrKN3UYF8fhUpVwG0dVxMUzVaQYTbj5E9i4xJLJ195+00XbijAKMHtOx4x0On0K3I+h7I1ScRFwgQXj4+es7Cr6UtecufM+h8nDb8NWwiNYEN6uft3AgvArNBUXGmAp+l2ift1YsrRz2uuv9x6ERewroPuj1DpN/iXu3z0bNqzvuviiVRtVG/Vo2imDDGgaJ40OeOFiHOxaXE10+CyWW2MuS2gar5lvNMJoNsPGTNz043Ax+NScbQjxRKNvuJiRI27joltFNZpJjrgYfGqsEokZfzn45M/RGUlgkk1HuQCLwROgi1H2QalrMdjasXDRkulz2+d/acuWzQ9hMbgK0qEo9bxmdhgWwgVtbZM34LFbdepps6eoPqrRlAVBhjIHt3HMIBfjQNcSmsYhmkljuM2QPxGUi0cNzMk3UWqMRVpYi0bPxExLUbdRbkxklIgT4hflW9UQ49kahZr2QdhocR/GJC6Cw1HyQeFfhYwQzpjdvi9u7x/hnorS8IvHWzNwFLN/Npu9Cff/mziFebPKg8EpEyZMWNcxb+GnlI9axLoghAO82oB3OYvkGsWqYiCmD2smbnR6yq2JHmlhLbrmuNtQY8xyMeZqUU6IX5Rv46qJTnPizBfParCiPqwxl8XhzjatqfQhDx38tRmgw472joVH4jz5JkyGPVQaN8DkPQGH/DfCjeuDYhPwOP4Ii0yX8lGJWBYEO5QbGfApyY14uIXkhgxm4kYv0ViL7nBbi26yjWoilW4jK+pWDb2ifBtVTXRrGpd8esppojlcjLksDi+zDZCekm49RLxhBA6T/y6RCL4Pd1wdFRDz5i86GYf7F8ON/b5jkenAYvNLpaMO8SwIMrCdwSxmdYfbuI50U1uNueqLmXi1Pky+4WFNrY58Y8zV4mqiwxfdFjVqolvTuOQ73JrkOlxyWRzubiP9OByG04Zh/Y7D6WfM3R234wa4424xaO+Y/+9YDM7D/W/aOT+OFP4Ri8IPlI4qxHuEIAbOAT1gwMOKBrtqtFCjqU+tZh/WmMvicDfOWNn8Ek10+NKPcmvMZQlN4zXzraa+5DrcxqUfh4vBR8UPKsEdNrS0tFyKZtwtBpikb8cjvgpu018wxaJw3Gh8TSGmBUELqoEDHlY02FWjURPdmsZr9mGNuSwOL9pG46EpL9VEh8/ibk9jLktoGq+Z72iSz6K+uw01xirmkyV2YDUcaO9YwE9I8pX0etGDwf17tL+pVBB/A+2oxmGHH8EH+usodS+EuF/r8T+6D+4t8O9Am5VAncCRyGULFi7eRemogIy2oeK6A0+QzyHo4A075YCWVmq2ylVoPN/U0qIasL3WZfPpiRNxwkw69bXWtGIunqncHsIc0Q1sXGrRHS6tiCGPMuCpQyXUYJlUcsZbbjyvV6WmYW77/N/iMfmA0opADifB6Su6OzkhGsZo+xzC7Dkdn0yn0z9WWgu34n9zYSqdvnl551lFi928+Ys+gInOt4rruhwAHsMrVq5YfqzSEUfMpwz0ZbCEE80Mao2DmIljzcRL8200yjearVmZDBtTLv04XAw+NcaUE+KL5nDRND80+qppHyZfc6gxZrkYc1kcXiZfFfFNfqSIRtP8N3L9u8kmTQQm0z7YX63FgL9SdXJ317IPD3YxGG1Y3rUSa0F6rtJq4IL8tYcffvAj3d2dV5UuBkTX8rN/h8fls5jofLv2OZUrAjnH4HHfVemII+ZTBh3AylmLgbCEXDxqjDncGogU1cJadM0BJ8SnxpjlYvXmW80Q8cU0Rk37IIwOK+rDmMRFcLgUmJOviviiie5ooosY8kwiuR2apgL7PEzdikil0t0Y8HwFfsygt7eX7+LsZ1h5YILz04Yn4L5fcu01V+eMWhl41r+XiwLcWotCEkdKJ6k/4ojpXQYMZBb6RjHGAc0SmsZFj3gYFz3Swlp0zXG3oUZiudjAfEJ8zZccq9FCjWbg9iFcCqyoD2vMZXF40TbGVya+yY8U0USHL/0o17ol1fg3ShtFPp8/UN1KeDKfz61Uf8wARwefULci8D85C4tBQ19LR35Pf39/zXeIcIrxeXVHHLEsCASHrWk5oPkAqi9m4kaPNEI80R1ua9FNtlFNxEwah4uZBNOPcvGogTNmuTVqolvTOPPFU25Nch1On5rmm5iTQ53EcmlRUBnuavClH+XWmGuEVtRNBZ6pql4+HwP3J3jma/rrGMMN3K9an/O4D/8bvvPSMC44/5wnksnUt5RWAj8ePSpOG2J+DQHGARwafTOgB04aGDXGivpgLovD68ov0USHz2K5NeayhKbxmvlWU19yHW7j0o/DxeBTG7ANTDSH0yQ34qlEsoBwszFT27LAgsF3E8YUTjzxpO3RVJ2MuN8/6O5atkFpw9iyZdMCdSsCRyn/qO6IIqZTBqeIsdUCsViDUQMJuRhzWRzuxhkrm1+iiQ5f+lFujbksoWm8Zr6jST6L+u421BirmK+8bL7V0IpmzcRwyrAFTdMwZZttOBbaDCsPnBO/rO6YwfQZM96mbkXwyEjdQWHVBef14H/NL4ZVBPYx6KuOxYn4jxCEc1DDZ7GcJprDxZjL4vCibTQebqNcNGsaZx8slltjLktoGq+Z72iSz+JwG6fG2KDyVaOFGk19aqj6CrlBP0PFCL7DMKaQzWZrTcR1K7o7n1J/KLhH27LA/3hndUcUMS0ITpHB7gxoayCuRlCjazJsTLn043Ax+KJFnBCP+Q4XM3LEJaZaUb6pqZOYxhp8apKv3MapMQauivE0KeRSmMtiuWo0aqJb1YD5lvcX8mtE9IgVra0TJqpbCbF8qApHAH3qlkWhEMQyF4eKGE8ZOLDtkDbDWExikRbWolmL4sWTxhp8aowpJ8Qvyrcac9UX05joVlGNRo0xy8WYy+LwMvmqiG/yI4UaH+Cyt5FGTXSralzyHQ57cmPvOrgeMaNQyKvnQcR4yhANXjEQM9iNFtaia46zDQOMETYqMQlFnBBf8yXHajTRrKIxatoHYaPFfVhjrqkMM3FpnXzWNkM00R1NdBOgT4RxI4sf1dQYc7g1rAeH/99/j/qP/zaIqqcfQRDwIfAYZsR4yhAOXh3sRgtr0TXH3YYaY5aLMZcl4oT4Rfmq0STf8ihO0ShWgxX1YU1STczy0m3gKxPf5EeKyaUGX/NNUWMuCyyqqTHmcGsgLOlk6hHIYw2va1sWeDx2VLchYLuq5+KID8e7NVstYjtCkD/TGG5r0WV4q2oiojFmuRhzTTGqgcSK8lWjURPdmsYl3+E00RwuxlwWh1fdBi25aNY0LrkOt8ZcFlhUq1Y132iFIKj6gtTWiHQ6XeuLQNMXLFrS0Hvz8+Yvmo5ji6of8c7n80UXe/UoRnyvIbB1a2oy2K1qIgMnGI25WlxNdPii26JGTXRrGpd8h1uTXFdTX3SH27j043Ax+KI53M13OY25LKFpXPQSjSa6w8VwnhsUfodmTKFQqH2fctlsox/p/XIQJKr+6hX2u1pdjzKI8TUEM3jLD3bNYaxsfokmOnzpR7k15rKEpvGa+Y4m+SwOt3FqjA0qXzWbH5rGqNXswxpzWZKvbz9h8p2gYwr6icenDauIr7R3LKjrEmZz5s6bhcneobQs8Fi+Onny5CFdgn2sI5YFgSg/2FlgAwa8+qJZsxp86Ue5NeayhKZx0R1uTfQSrShfuY1TYwxcFfHryQ81GjXRqWpMNJuhGo0aY5aLMZfFsFQi+euWq5eMuY8LK4ouzV4GfLb/NU4F3m1oeXTMW7hbJpPhFZFrfd/jtrOWntnUD3ht7YjplMEZzGGB1THgTUy5aMqtSa7Dw3wWq6hGE93hYqppvolpnBpj4KqIX09+qNGoiW5VjVN0Oa2oD2vwqTGmnOgvVP8BnK0ZmMTL1a2GbfHMfx8m/XmnnzG36GIiJ37lpB2wWJwZBME9yNlL5YpAzkXqelRATKcMphAymBsY8OKJZrmppWUoNBNz+9AU8amRWDWMU9N8KqbAqDFmstSYq0WYjVMT0eRIUaMmulU1DtHsV7mt2YhnalFRubfRIkgkeqa3TPq10jGHzmVLezBJf6S0KjDpT29paXkaC8Pque3z70C5f+rUaU9g+6UI1/wmaBAUbsJpyq1KPSogxgUBJpPA4WIc7CwRJ8QvyleNJvmWa0w0q6hGo8aY5WLMZbHMiTv5qohv8iNFNNHhs1huazQ2P6qpMeZwayAm39E03ygDUQiCyyZdO/AiHGMJqVSKv4RUN7Aw8AKwB6C8E3SyUasD26xPJlMLlXpUQXynDM5gDwc4NdGjAS9+Ub6Nqya6NROnaJjhwor6sCapJma5s43+KdM4NdEdTXT40o9ya8xlgUW1alXzHa1Mfhn0ppPJb6s/ZrGiu7MXj8PRSpsC9H8h9uNfTKwD8R4hiPEfoCVU1OcEEN0WNWqiW9O45DucJprDxZjL4vCq26gvmjWrwZd+lFtjLktoGhfd1dRE15zQVHPyKyFIBN/f/vruOL5UM+rR3bWMLwjWumbAYPGf/f3Zs9T3qIGYFgR3sFuumujwRbdFjZro1jQu+Q63Jrmuhpaa5Cp349KPw8XgUyvdRnIdbk1yHR7ms5RoNNEdLqaak18DeNZMn6f+uACewb+EQ/sLlcYCPN68qMm8C85f2dDVkMczYjpl0BIaffmH6CRQbo25LKFpvGa+o0m+5TamXPpxuBh8aoxZ7uaHXDW2qCwnQq1SH4xZLsZclojXA+Sfu/11y2u9Rz/msHLF8lOxKDT0mkIF9KKfOdls9hSekqjmUQdiPEIwA95MAvgyCZRbA5ESmsZFN5wwOkx0h4upJvnKw3wWw1UxHrUa+aFGoya6VTVesw9rzGWJeL1A7t2FIODvA4xLYFH4BiYzL1ryX0ZpGLcWCoUPo59zzzt3Rc2LoXoUI7bXEEwLk0lgNDMZqMFnCU3joltFNZpJjrgYfGqab2Iap8YYuCrim3yjmIhGnfxQo1ET3aoal3zDiTCORj015rJEvEH0ppOpL8+8vntcP6thMq/BM/sJhUKwHyY3L+r6qomUBx7vV7CIXIbyHmz3oXNWdt2rIY8GMYgxOxB3H3zSMYUcf6jFIJwMnByhYhDpVnFyVAq59VHZfFMrN3+KqMeoH+NEupOjtbSoLI9qtNpRyG1cBfIoV+qQNwpsmUcnx2933fIfqjSs4CXUTjrpFB6yq1IWP8SEe0n9YcVnP/eF6dtvP/NDqVRyJh6tNvxvsps2bVo9adKkp39y5f8+vmbN6kFd2GD2nI5Z6XT6n5SWQy/u83fUHzTmzp33kWQqxbdKywL35/HurmXXKh0xDHb8FuHuQ046JpBfbiJ0UqAq4vQ0EHKtowlm6jAuTmm+KubPMuOpY5VIL+E2rkLj+aYO4+JEfHBItm9/fdeYu8S5x9aF+N92BJESmsYhFnEaNclVLsZcFodX3UZ90axZDb70o9wac1lC07joDrcmeolWlG/4YIAt+ZS82C8GHqMB8b2oKJNDfTH61BhzuDXJdTW01CRXuRuXfhwuBp9a6TaS63BrkuvwMJ+lRKOJ7nAx1Zz8IaC3kAi+tP313f59co9RgfjedgyNvk4YmTTKrTGXxdVsvvXdbaQfh4vBpzZgG5hoDqdJrsNtXPQSjUaNMbePMvlDQ/KZdDL5bzOv7x7zn0b02HoQ49uObN1JY2BiMNE1JzTVND8qMGqMgatiPGqSbxRTYE5+qNl85YTxqZuMkNOK+rDGXJaIDxXo69cTMy1/P+O6rl+o5OExKhDfawjOpDGafJdfdc0JTTXNNzGNU2MMXBW5kdRSNfJDjUZNdKtye2qMWdVEivuwxlyWiA8Vfflc4vaXnlr37UfvOmXKNWfV/GVgD4/hRhzjPHH/oafIuwz0TYeYQNpzyK2Pyk4vUys3f4poAkb9GCfSnRytpUVleVSj1Y5CbuMqkEe5Uod8qGA/z258PbjxuceDDdk+rEtY5JLJVX1BbmXXM3e8aLJGHu0dCy5DE97tVCp1b9fyswf1m4YeWyfiO0KQAuNEBQm5GHxqjFleJl8V8U1+pIgmOnwWy60xlwUW1dQYc7g1EJNvNeWSa3gc2JLPFX7zwprClU88kHAWA+7r1LZU63PL3/rhJZo6otCfcvuCW/L5wkfReowjxPcaghnkMpGEixVPMpNrIApjERPf5EeKaKLDl36U21qFkNt4mXwxECmupvlGiQf5oBA8/Nra7OWP3pW4/5UXU1gE5NaYxSA8neLjv7h7t4Mf6t794H3Mlh4eI4d4FoSyE4zF4WGBUSexXFoUVIa7GnzpR7k15rKEpnHRHW63Ed3hYqo5+XGgZ8vG/NVPPZz/5XOPtfTn81wMZG/RYmD2aRYFKXvBv/e8tx36RdODh8fIIJYFgTBD3p1gysMCk8HvcDH41AZsAxPN4TTJdbiNi16i0agx5vZRJj8O9BfyhdtfemrLFWv+nH5qQ2+G/RYvBuYB537tYmDiJg+47MI9DqvnOoMeHk1BPEcIYjrJrB8WGAe9xGycBp8aY5ZXy5dch9t80Us0GjXG3D7K5MeFFza9UfjR6j8n/7D22YnZQl76Ll4MnEXAthIvzgsSiXkX7XH4mL2OosfoRiwLQvh2npgzCakxZrkYc1kcXjZfNZsfmsao1ezDGnNZIh4X+FbizeZFwyROFZJFi4BtUaodGQzMSxzy9b854jb27zE4zJq1R5z/5nGDWB60Rw47/ZhE+LYjZ57bsRn44qljFdal+TYibai7NVrtiLX1or5NrVT1iMeJZzb0Jn79/OP5V7dsTtee5GyVS7yuvFv/4y+/+BDkpoPvMnz1qyfz+gHhQxUEietXrugc9e80zF+weJf+/r5j0uk0L8D6t0EQ/BVkXoAVNPkE+P1o789kMt9bdvaSl2WjGpg9p2NfbNOObTemUqn7IH185YrlB0G/KpVKrlq5omtMXsE5liMEjiAZ2jKw7YgSRXzRRHc00eGLbosaNdGtqnHJd7it0VhuDD41yTU8TvCo4IZnH8vhqKDQxMWAeQd95x0f+xlCHmXQ3rHgoI55C+/O53OPYTHgl8O+jAnMX3raAYULQhv43miPQ9udzWZfmts+/6pTT5td89egzj2n+0/o83+wGNxQKBSez+fza7HdV1taWibgP1X19yO3ZsQyVx477IxjEjn7gyIykI2njlUivYTbDFRuJIyXyZdWBRsN42YyNQU8Krjm6b8UNub6U4Oc5A3nAbO/8PA1Tb3GYqNHCHimnILJMgu3911sc7ncjmgngm/C5HsRk/SuZDJ13zkru57XTWIDJvXuaC7EvgZ99FLI53+QLxRmn3/eyorXd8Bi809YDCbiAdkulc68BP9SPCpfxH5ndXctW6VpYwrhP38oePzwM44JsvnoAinq6GAOd8LBLq3UTlyFxvNNHcbFiXic2JTLFm55YU1w/6svpTlRq09ycBuvmsc4b7fJs5rNc7eFf9DxD/68aa8r1LsgLFy05P2Y/B+Hewwm/luMWhmYRL/HQnH9tddc3fXwww8O+afY581f9Pfok98BqfnjLHXgVdy2w7qWn32X8iKcdXbXm7PZ/jTc1v7+/nXI3Xvy5CkPvvD8c2+69NKL/2KyxhbCf/5QsPrw2dEFUlCZIR11zkEtrdROXIWB+VJH3MZVUBbFxYl43Hikt6fvV8893rIJRwV28tqJyn2aVjmEMB5DnrxgC0snUz07tU7e/ZB7vr+etylu1FoQFixcvHNfX99iHEZ/CnQqtQaB9SNxNvpbrLxhzF9w5kE4dOfvQVZbDF7DY7kaO3sDpRWT+J1oay0eH1jR3Xm7+uMa4T9/KFjDBUEuoWa6s51ykEsrNVvlKgzMlzriWkf5pg7j4kQ8brzevyV30wtrko/29qS5j1qT18Qbz7Oazauy7c+Pu/+nfHaOHdUWBJwefAoLwTcgxfGsfB8m6afxrPyw8rrQ3rGA+34CZYYIDjDhX0Cfl+DI5Wqc+w/o94TPfn6nHXfc6Ti47Sh8faEUr7e0tBy47OwlDyoft+C4HDLMYDaD1xSYDuZiDS1LaBoTvUSjUWPMcjHmskQ8bgQYYnf3PL/58kfvTte/GJgHs3Ye48V5Upy8KtsefcW7P/F+yMOEYBrO1y/BYsDfX4xjMSD2wSH/ne0d8z+ivC7gvvM7HwMWA+AcxN6Bc/qucosB8b3vXv4SjgDOb21tfRNyv6myi2nZbPb76o9rcMwNGU8eMUdPGdCd+ROY1gzsSI9qjHHxjBJFjO5waeGJE/Fm4JW+Tdkbn30s8fSG3hZy7ksmKPfLFoVayUQd9GLg5tWzbSqZevKT9/049le5yx0h1ABPXfiry9fgMP42tC+0tbVtRjsVz9jvReytuM0nwp8l2SVADKmFw1auWF7zQ1hfO/m0bdH3arhFCwKOCjpxpNHwbzbi1OMM3OZzlbo4DgtHXT8+O1ZR7z+/Kp7igpBzXlTUWlpUlkc1Wh304msNST1TR7lSh7wZyAWF4J6e53N3vPx0C99WJLg/MxF526pP1LjyijRym+tsGyQTn/jkvT/+KaTY0MCCkMVEvG7Tpk1nXLjqPB7CVwWOMHil5Itx+vEOlVz0ZTKZ93UuW/pn5WUxZ+68z2CfRc/gWGiumTlz5sfnzD5tUFdb7pi38HL08TmlAjy+P8WRxieUjktwnA0dOojFtQZBCiyqqTFmOBHGVTBNSb7yZuHlzRtyP33iwcLNL6wZlsWAmptXTivqs3QfieSgX5gbCrDvV9D8K56Vj65nMSBwBHBLd1fn3ti23DP5BJz3X6N+RWDR+Dt1XVw+2MWASKczp6FZZ5gBFoiPzJq1RzxzYitFLHdeJo81ECmwqKbGmMOtgZh8R5N8U7FpFvJBofDHtc9u+cHq+zJPrH+Vby8JzK6dCai3w7TKIQxmMWArxckzmtlvuK3q5faRTibfeeV7/nUPhIYTL6bT6YNxSM0fZm0YeObtxIT7jFIXu+DZuuo1IXB4v426ISZOnHinuoNC57Ilb+CU5Yu4TfOd0j1jxoxwHIxHcAwOGc98tD38YBIHs2kNOIilldqJq2CjYVyciDcLPVs25n7z/OrgqfWvyWsFFtxv8QQ0t6bWJDfx2otBubxyWq1tgW/88z0/iuN3EAU1Thn4k+1HYVIP+XMQOH9figl+plKLNzDBZy1dsmit8iLglOHbOGX4vFIBJu+uOPoYd79/2WxwzA0ZHJ9mKJsBK4WaDmBT1EQv0YryDW8WCkGQu7PnuQ3ff/zeTO3FwNyaihPVcrbQKuap5uaV04r6dLYNdWcf6WTqWNBhAZ8541gMiOWdZy1Gf6UfBJq6efPmovN5FzgyGfBTbnhMLlHXI0bEsyCIseU/ygzkIo0musPFVHPym4n12b7XfrTmz703Pb96in2twMLclsoTsOxEtfqAPPPAuv1J0bxoH2a/4bZWL9m2/D6S0694zyfKvVAXN57Cs3O5t+qGggGLGfYxW90BQEw/Fl+EI9s7Ftw2t33+rso9YkBMCwIHsBnExlSjyeB1uBhzWSLeZGQfeu3lF779yF0zntnQu71qIcztqTkB652oUVw1N69425JW4vXflhktkxp6L3+Q+C8cHcT647P8MVc0DxhmgKOG7WbP6Sj7diqOKv6Epihf8Q94LJ7EwvCLjnkLT5w3f9Fwv64y5hDPgqCDVSaWFDNo8RdxMeayRLzZwJFA8ItnHum95um/7Lyl5KiAMLepvgk4mDwpTl4j29bKyyRTB8JtKgqFwn+rGzOSF6kToqWl5TB1BwD392g0lX6J9qNYUC7FbX0Ui0MW5arZs9tXYZH4yqmnnXHkmYvPervmedRAPAtCWMyAxV/ExeBTY0z5cODlzRsK33n07s0PvPrSTJWKYG5X/ROwkTxqbl45rdK29e4D7XtAm4mHz1nZVdfbi41i8+ZNvMZAEfr6trxV3QHAUcqadDp9AO7zZpUqIYPysXQmcwoWia9PmDDx2r6+voexSARz5s67C+23UD5pUj1KEduCwBrj1HpqHLxmAFs+XHi4d23/D1bfl+jt39KmUhHMbWt4AtadJ8XJa2TbevMKQbAjpGaiR9vY0dY26XF1Q7S0tFb9BCZOHf6Ao4i3YaIP6qgllUrth4aXmP8xFoUcyqpzz7uwVYIegngWBBmwaOmLGRgt4sOFNW+8mr3hmUf5IaOy909upzOx6p2A9eRRc/PKaWFfbKvtw3K2ZfJwyjD5xvf9W9PeN8fE26Ru7Oju6nwdh/hZpQZBwIuaVMXZZy1+YeWK5f+eTmf4gup5uI2DfeuRj9sp69b1bMLCwNMRD6DshGkUHMAcxsY4cM3gNWx4wdcMfvnco6n+Qr7szs3tK55Y1EyrXOKDy5Pi5JXd1uq19lEjD01iY65/MF9FLgeenxdNUEy2WMZHORx+xEfxhJ0q7j+ZrPuTh8s7lz68ortzNhaHXfP5PC939lnIS3O53E/Q3i1JdQD3kQvDzzrmLSz3oalxh1j+4Wb4mgHKAWv5SOCR3p7CG/19ZZ81zW0cOLHCCchW4o3nUXPzymlhX2yr7cNyttXyYDMnTOE585CxYf16LghF11rA/nZWN3bsu+9+fEeg6P+E/Q3q9y7PPaf73u6uZd/DArHkvHNXfBLt36Kgu+QuCB+NdhHaqtdA5GmIfwsT40rbIQFjUwarsZHFcxtfV68YvF28jY1M8lp59O3Ep+bmDdiW3Oq19lFvHtrWZCz/QotntbXY/dOfOb4p59h9fX3lfqnqSW1jARaJZ/lRa7TL0H6IiwROU47DY3mPpriAPDLfERlNiG00caCOBrSm0gPuE29brYll4o3lhTksmsdtpXU0s41tq+zDcrbV8mA27971L70BOS4UPYui/7ZddvlrXiEpdrS0tByibgjs7yF1m4ZzVnb9CAvEfthXucl/lLbjFgMmz9aON00uPqXmJJIJVWNiNboYMC/MdfLIpbjbql5zH/XmsUXJJFPZ/7j/2j6E4sKAw2qcn8f+glt7x4LpeKb+F6UWr2/cuPH/1G86sCicheYPhoWYfvay7rguBLNVgmNvTOFvps0M2jItcjFPTqJ6Jla9E7A0z9VsnpQY91EtD2e+/MRfbJg6ddpv0BR9KhH7OgoTONbPO+B8/Qw0RRMP+7nuogvPL/o6sgX2fyjKl9yioSEBt+MxdUNs2bK57NvU4wVmXI0htKRSqY/usmeh4cXAcrbV8lSTUkYLt7WcrZMX6jX2UU8eVr1YPzS0YP7cjWi+ZVgRYvttiLnt8/mOwElKQ+CI4XJ1BwD5/AQjv08RlnnzFx2PdkhAv6WvYwS/v+P28i9CjRNwbI05vG3qdpn9d3hLoaEJaPUBeeZBCvNEY7RYG7Ct1WvlsZV443ktyVQzLgW+HP33q2+xa8e8hb9Uf9A49bTZu6Fvvi1YdHSAZ+qrV65YfrPSAchls79XNwQWkKXqDgpYUA5F8y7DDHDb7r3llpu4KI5bcHyNSXx4591TJ+zx3sKe02fKBxIGPwGjlpoUzWtk8jYjD4j90uErujt7Mdk6lIbApP1HHKrforRh4MhgnwkTJvCUpPTjyTxF4fl8RaTS6RvQlE5ULlLXqt8Q5sydNwP38VKlIXAfB9XfWALH2JjFzEmTU0fusmf6qF3f0T+tdWJhqBPQ1cTIxY9vkjeQF6Ad8H2AOIBn6wvQlFtsDsKicN8cHPYrr4nO5SsmY5sv47ZyMRnwXQVMwmXYH7/NWBGIczFYYVgEbMuvQN+0eMmybVWqCZ6ypNNpvnjKX39ywYXwB+qPW8jTzFCx7mMLjklk8+W+sz6q8NBrL2fvXPtcqq+QSzcyAatMyprbNisP/r3v+e036p6YjQITjYf1d6DsJcJA/Bw344fdXZ08BRiAr5182naTJ085NggK/O7Au41aDEzoCx944M+n33D9dTV/0WnlOedPeuWVV3jqMODzC3hM+tEXn/EvwBHOM0aNcOihh6X2fe9+B2DCfwK5/w6p3DsJi7Ft1SOV8YBxtSBY3PfKi4W7ep7jT7djTNc7AY1m88w2uq3EbTtw21gWA1c3eSv3ue0b/OGRpuGM2e0zMpnMb+HyB1MrArfoziARPItJmcVt3TGfz78Zz8I7IVTtY9V88XIuT1EMrQ2cIuyESf1H7IOfQCwLxPmjLXfhtmwBbYPPT1vuBl7uNx0EiF0xZco2Xzxz0bwNKo1bcGwNGVvbgkDkCoX8nT3PBo+9vi4TTjR3ApbTyK0OLYqX5FnOeKN5sCg/2m/pti3J9AHvuPWSpr9vP2/+mVPxLP8zTJqDVRoq+tDXwrVrX77ge9+9vOGrJs9fcOYumPQ3oI9KRy4NAY/lVejrs40sTGMZ43ZBsHitb3MBpxKJpzb0yjdtzKTTyYdSOlGLNHKbW8e2Meb96d23XcofQxk24BTiVDR8bWEouBdHDu3LO8+q+eMstdDRseDiIJEY8PZlA+ACsHS77bb71tw5p4/rdxZccNyNa8yYMCl14E67pg5986z81NaJOU5ATjopiIe+lqLJy5o6tCqT17QSbzDPctVMi6ODVOpK0GEFnkFXrVu3jj8B3wXa0Kcj8QzM7w6civbDcSwGRHd359fw2PADU43+BBuvIH05fyCG98kvBsXgeBwytuYjhFKseeOV/KO961Jb8jwdjiaqTE7Ew0nKiLTNWwxK96F5vRty/bu9//ZvvQZ5xDB7Tse/YFJ9gF89xrP+vpjsvJZBgMP5fvBXwB+C/ycsIFfc+cc/PHDLLTcN+kdVauGfP3ZU21577f0F3JYPYn/vwmPF1wz4sOXh8/cX1qB9ELFf8XTDnx5Uhl8QKmD1G68EOJUIMAlT9UzeUK+WR5WtxBtbDGxukAjOetetl466b+Ude+yn022TJ7dhMchd9s1v1LrMWdPxuc9/kbcl+a3L/tMfATQAvyBUQT4o5P/S21N4ev1rLdGkLZmoljMOzU7cKL9KnqvbvAqaGI4O1vVvfPtBd3z3JYQ8PGIHx5xHBaSTqfTeM3ZsOWjn3fJvmTwdx6BlJmo4YQdxZGB1p79SzZqJJVb5xcCjmeC486iByZnW9N7b7ph8/467FKa1TsyZCRtN1KqLgeVsbZ6r2zxuyx5czS2J5BOFIHEhQh4eTUM8C0K2zA8ejEFs0zIhtf/Mv8rsNX2HYFKmJZBJDd20ZuKWTuhQt3kSL5MXxoxmTbcNMqnUyXvfeol/McyjqYhlQWhNpEb0Fe/hxk5t2yTft8NbkrtP3ZYTla9kO5O98cVAjg5KNS3cFqcuF8666cLr4Hp4NBWxLAj9iULVL6eMVezcNhULwy6JN7dN1dMIndCc9DrJqy4GmkefeaY15mz7pyARDOmrvh4e9YJjLhasPbz9RQxefn59XKI/n8+/uHl9+tW+TaUTuvxiUEGj2W2hrc0VCge+89avD/hREw+PZiCWIwQCh7U/VXdcojWdTv/1lOmJPafvwNca+htdDKzZxQBtL9rj/WLgMZyIbUFoa2n9jrrjGpPSmcTuU7dtfcuU6X0T0hl5q9IsANWPDGyJFoPkZ/e8+eIb2aeHx3CB4y829BzRcQc6PECpB8AvT63bsqmAuZ4JFwIWxMyiYDS7QHAxQASLwUVXSQceHsOI2I4QiM357Mnqeij45alZ07ZLbzthUj8mvbxVWboYWC2VTK2dmMoc6xcDj5FCrEcIxLojOvgVWX5V1qMEuaCQe71/S3pzLpt0FwP+E+D/LgiCT+91yyWlv57k4TFsiH1BIHqOaL8Nw/wflHqUIFvIB+uz/Vm0rVgYNqZTyfMLQXD+njdf7D945DGiaMqCEHxy5cRXN752U5AI/OsJVYAjhV/19G1cuO9t/3mXSh4eI4qmLAgWPUd0XIodnKjUQ4GjgdWZVOriIEh8b7vru+L8bUYPjyGhqQsC0XvkgqOzhdwqnEJUvDDmOMKtyWTySpwm/HDGdcv96YHHqEPTFwSL3o/OPzEXFI6B+0GjjH3gSGBzOpl6KBfkb2xNZa7EIvBnDXl4jEoM24Jg8csDjm/ba5uZR01MZf4Gh81/BUne+sTk4W2xtycZaJtIiK4+dBOwuWGpkG9bvqpPWG5RLrdaSxT7IUvmCoVCXzqVWgfpOdye3+aD4MEdru/u0QQPDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw8PDw+PYUAi8f99nZwydhAtkgAAAABJRU5ErkJggg=="
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  [data-testid="stSidebar"] {
    background: linear-gradient(160deg, #1A1A2E 0%, #16213E 100%);
    border-right: 1px solid #0F3460;
  }
  [data-testid="stSidebar"] { color: #e2e8f0; }
  [data-testid="stSidebar"] .stButton > button {
    width: 100%; text-align: left;
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
    color: #e2e8f0 !important; padding: 10px 16px; border-radius: 8px;
    font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s;
  }
  [data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(233,69,96,0.30) !important; color: #ffffff !important;
    border-color: #E94560 !important;
  }
  .main .block-container { padding: 2rem 2.5rem; max-width: 1400px; }
  .card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }
  .rank-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 36px; height: 36px; border-radius: 50%; font-weight: 700;
    font-size: 15px; color: white;
  }
  .rank-1 { background: linear-gradient(135deg, #f59e0b, #d97706); }
  .rank-2 { background: linear-gradient(135deg, #94a3b8, #64748b); }
  .rank-3 { background: linear-gradient(135deg, #b45309, #92400e); }
  .rank-n { background: #ef4444; }
  .pill-green { background:#dcfce7; color:#166534; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:600; }
  .pill-red   { background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:600; }
  .prog-wrap { background:#e2e8f0; border-radius:999px; height:10px; overflow:hidden; }
  .prog-fill  { height:100%; border-radius:999px; transition:width 0.6s ease; }
  .section-header {
    font-size: 1.4rem; font-weight: 700; color: #1A1A2E;
    border-bottom: 2px solid #E63946; padding-bottom: 8px; margin-bottom: 20px;
  }
  [data-testid="stFileUploader"] {
    border: 2px dashed #fca5a5; border-radius: 12px; padding: 12px; background: #fff5f5;
  }
  #MainMenu, footer { visibility: hidden; }
  .evidence-box {
    background: #f8fafc; border-left: 3px solid #E63946;
    padding: 10px 14px; border-radius: 0 8px 8px 0;
    font-size: 13px; color: #475569; margin-top: 6px;
  }
  .desc-box {
    background: #fafafa; border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 10px 14px; font-size: 13px; color: #475569; margin-top: 4px; line-height: 1.5;
  }
  .comment-box {
    background: #fff8f0; border-left: 4px solid #E63946;
    padding: 14px 18px; border-radius: 0 10px 10px 0;
    font-size: 14px; color: #1A1A2E; margin-top: 12px; font-style: italic;
  }
  .stButton > button[kind="primary"] {
    background: #E63946 !important; border-color: #E63946 !important; color: #ffffff !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: #c0303b !important; border-color: #c0303b !important; color: #ffffff !important;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────────────────────────────────────
defaults = {
    "page": "RFP",
    "companies": ["Empresa 1"],
    # ID interno estable por empresa — no cambia al renombrar
    "company_ids": {"Empresa 1": "empresa_1"},
    "active_company": "Empresa 1",
    "pipeline_results": {},       # key = company_id
    "rfp_bytes": None,            # bytes del RFP — persisten entre pestañas
    "rfp_name": "",
    "company_files": {},          # key = company_id → lista de {"name":str, "bytes":bytes}
    "rfp_criteria": {},
    "edited_criteria_hab": [],
    "edited_criteria_cal": [],
    "criteria_loaded_from_rfp": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de empresa
# ─────────────────────────────────────────────────────────────────────────────
def _ensure_company_id(name: str) -> str:
    """Crea o devuelve el ID interno de la empresa."""
    if name not in st.session_state.company_ids:
        import time
        slug = name.lower().replace(" ", "_")
        st.session_state.company_ids[name] = f"{slug}_{int(time.time()*1000)}"
    return st.session_state.company_ids[name]


def _get_company_id(name: str) -> str:
    return st.session_state.company_ids.get(name, name)


def _rename_company(old_name: str, new_name: str):
    """
    Renombra una empresa preservando todos sus datos.
    El ID interno permanece igual; solo cambia el mapeo nombre→ID.
    """
    if old_name == new_name or not new_name.strip():
        return
    old_id = _get_company_id(old_name)
    idx = st.session_state.companies.index(old_name)
    st.session_state.companies[idx] = new_name
    st.session_state.company_ids[new_name] = old_id
    del st.session_state.company_ids[old_name]
    st.session_state.active_company = new_name


def _make_file_like(file_data: dict) -> io.BytesIO:
    """Convierte {"name": str, "bytes": bytes} en un objeto tipo-archivo."""
    buf = io.BytesIO(file_data["bytes"])
    buf.name = file_data["name"]
    buf.size = len(file_data["bytes"])
    return buf


# ─────────────────────────────────────────────────────────────────────────────
# Helpers UI
# ─────────────────────────────────────────────────────────────────────────────
def color_for_pct(pct):
    if pct >= 70:   return "#22c55e"
    elif pct >= 40: return "#f59e0b"
    return "#ef4444"


def render_progress_bar(pct, color="#E63946"):
    st.markdown(f"""
    <div class='prog-wrap'>
      <div class='prog-fill' style='width:{min(pct,100):.1f}%;background:{color};'></div>
    </div>
    <div style='font-size:12px;color:#64748b;text-align:right;margin-top:2px;'>{pct:.1f}%</div>
    """, unsafe_allow_html=True)


def format_currency(val, currency=""):
    if val is None:
        return "N/D"
    try:
        return f"{currency} {float(val):,.0f}".strip()
    except Exception:
        return str(val)


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────────────────────────────────────
def run_pipeline_for(rfp_bytes: bytes, rfp_name: str, company_name: str, proposal_files: list):
    """
    proposal_files: lista de objetos tipo-archivo (con .seek() y .read())
    """
    tmp = tempfile.mkdtemp()
    try:
        rfp_dir       = os.path.join(tmp, "rfp")
        proposals_dir = os.path.join(tmp, "proposals", company_name)
        output_dir    = os.path.join(tmp, "output")
        os.makedirs(rfp_dir)
        os.makedirs(proposals_dir)
        os.makedirs(output_dir)

        # Escribir RFP
        with open(os.path.join(rfp_dir, rfp_name), "wb") as f:
            f.write(rfp_bytes)

        # Escribir propuestas
        for pf in proposal_files:
            pf.seek(0)
            with open(os.path.join(proposals_dir, pf.name), "wb") as f:
                f.write(pf.read())

        orig_dir = os.getcwd()
        try:
            from utils.extractor import load_rfp, load_proposals
            from services.rfp_parser import parse_rfp
            from utils.evaluator import evaluate_proposal
            from services.scorer import score_proposals, generate_recommendation
            from services.report_generator import generate_report

            rfp_raw       = load_rfp(rfp_dir)
            proposals_raw = load_proposals(os.path.join(tmp, "proposals"))
            rfp_data      = parse_rfp(rfp_raw["text"])

            if st.session_state.edited_criteria_hab:
                rfp_data["criterios_habilitantes"] = st.session_state.edited_criteria_hab
            if st.session_state.edited_criteria_cal:
                rfp_data["criterios_calificacion"] = st.session_state.edited_criteria_cal

            evaluations = [
                evaluate_proposal(p["provider"], p["full_text"], rfp_data)
                for p in proposals_raw
            ]
            scored         = score_proposals(evaluations, rfp_data)
            recommendation = generate_recommendation(scored, rfp_data)

            timestamp   = datetime.now().strftime("%Y%m%d_%H%M")
            report_path = os.path.join(output_dir, f"reporte_{timestamp}.docx")
            generate_report(rfp_data, scored, recommendation, report_path)
            report_bytes = open(report_path, "rb").read() if os.path.exists(report_path) else None

            return {
                "rfp_data":       rfp_data,
                "scored":         scored,
                "recommendation": recommendation,
                "report_bytes":   report_bytes,
                "report_name":    f"reporte_{timestamp}.docx",
                "error":          None,
            }
        finally:
            os.chdir(orig_dir)

    except Exception as e:
        return {"error": str(e)}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='padding:20px 16px 8px 16px; text-align:center;'>
      <img src='data:image/png;base64,{LOGO_B64}'
           style='max-width:160px; height:auto; display:block; margin:0 auto;'>
      <div style='font-size:10px;color:#64748b;letter-spacing:1.5px;
                  text-transform:uppercase;margin-top:8px;'>RFP Evaluator</div>
    </div>
    <hr style='border-color:#0F3460;margin:8px 0 16px 0;'>
    """, unsafe_allow_html=True)

    for key, label in [
        ("RFP",        "RFP y Criterios"),
        ("Propuestas", "Propuestas"),
        ("Resultados", "Resultados Globales"),
    ]:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.markdown("<hr style='border-color:#0F3460;margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:11px;color:#64748b;text-align:center;'>RFP Evaluator v2.0</div>",
                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: RFP y Criterios
# ─────────────────────────────────────────────────────────────────────────────
def page_rfp():
    st.markdown("<div class='section-header'>RFP — Documento Evaluativo</div>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 1], gap="large")

    # ── Subir RFP ─────────────────────────────────────────────────────────────
    with col_left:
        st.markdown("#### Subir archivo RFP")
        st.markdown("El RFP es el documento base con el que se comparan todas las propuestas.")

        uploaded_rfp = st.file_uploader(
            "Arrastra o selecciona el RFP (PDF o DOCX)",
            type=["pdf", "docx"],
            key="rfp_uploader",
        )

        if uploaded_rfp is not None:
            uploaded_rfp.seek(0)
            new_bytes = uploaded_rfp.read()
            if new_bytes != st.session_state.rfp_bytes:
                st.session_state.rfp_bytes = new_bytes
                st.session_state.rfp_name  = uploaded_rfp.name
                st.session_state.criteria_loaded_from_rfp = False
            st.success(f"**{uploaded_rfp.name}** cargado correctamente")
            st.markdown(f"""
            <div class='card' style='margin-top:12px;'>
              <div style='font-size:13px;color:#64748b;margin-bottom:6px;'>ARCHIVO CARGADO</div>
              <div style='font-weight:600;color:#1A1A2E;'>{uploaded_rfp.name}</div>
              <div style='font-size:13px;color:#64748b;margin-top:4px;'>{len(new_bytes)/1024:.1f} KB</div>
            </div>""", unsafe_allow_html=True)

        elif st.session_state.rfp_bytes is not None:
            st.info(f"RFP cargado: **{st.session_state.rfp_name}** "
                    f"({len(st.session_state.rfp_bytes)/1024:.1f} KB)")

    # ── Proceso detectado ─────────────────────────────────────────────────────
    with col_right:
        st.markdown("#### Proceso detectado")
        rc = st.session_state.rfp_criteria

        if rc and not st.session_state.criteria_loaded_from_rfp:
            st.session_state.edited_criteria_hab = list(rc.get("criterios_habilitantes", []))
            st.session_state.edited_criteria_cal = list(rc.get("criterios_calificacion", []))
            st.session_state.criteria_loaded_from_rfp = True

        if rc:
            proc = rc.get("proceso", {})
            st.markdown(f"""
            <div class='card'>
              <div style='font-size:13px;color:#E63946;font-weight:600;margin-bottom:10px;'>PROCESO DETECTADO</div>
              <div><b>Objeto:</b> {proc.get('objeto', 'N/D')}</div>
              <div style='margin-top:6px;'><b>Entidad:</b> {proc.get('entidad_contratante', 'N/D')}</div>
              <div style='margin-top:6px;'><b>Puntaje total:</b> {rc.get('puntaje_total', 100)} pts</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='card' style='border:2px dashed #fca5a5;background:#fff5f5;
                                     text-align:center;padding:40px 20px;color:#E63946;'>
              <div style='font-weight:600;'>Sube el RFP para ver los criterios extraídos automáticamente</div>
              <div style='font-size:13px;margin-top:6px;color:#f87171;'>
                La IA analizará el documento y extraerá criterios habilitantes y de calificación
              </div>
            </div>""", unsafe_allow_html=True)

    # ── Criterios editables ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Criterios — Editar, Agregar o Eliminar")
    tab_hab, tab_cal = st.tabs(["Criterios Habilitantes", "Criterios de Calificación"])

    with tab_hab:
        for i, c in enumerate(st.session_state.edited_criteria_hab):
            with st.expander(f"[{c.get('id','H?')}] {c.get('nombre','Sin nombre')}", expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    nid   = st.text_input("ID",     value=c.get("id",""),     key=f"hab_id_{i}")
                    nnomb = st.text_input("Nombre", value=c.get("nombre",""), key=f"hab_nombre_{i}")
                    tipos = ["documental","financiero","tecnico","juridico"]
                    ntipo = st.selectbox(
                        "Tipo", tipos,
                        index=tipos.index(c.get("tipo","documental")) if c.get("tipo") in tipos else 0,
                        key=f"hab_tipo_{i}",
                    )
                with c2:
                    ndesc   = st.text_area("Descripción", value=c.get("descripcion","") or "",
                                           key=f"hab_desc_{i}", height=100)
                    nvalmin = st.text_input("Valor mínimo", value=str(c.get("valor_minimo","") or ""),
                                            key=f"hab_valmin_{i}")
                cs, cd = st.columns(2)
                with cs:
                    if st.button("Guardar cambios", key=f"hab_save_{i}"):
                        st.session_state.edited_criteria_hab[i] = {
                            **c, "id": nid, "nombre": nnomb, "tipo": ntipo,
                            "descripcion": ndesc, "valor_minimo": nvalmin or None,
                        }
                        st.success("Criterio actualizado")
                        st.rerun()
                with cd:
                    if st.button("Eliminar criterio", key=f"hab_del_{i}"):
                        st.session_state.edited_criteria_hab.pop(i)
                        st.rerun()

        if st.button("+ Agregar criterio habilitante", key="hab_add"):
            n = len(st.session_state.edited_criteria_hab) + 1
            st.session_state.edited_criteria_hab.append({
                "id": f"H{n}", "nombre": "Nuevo criterio", "descripcion": "",
                "tipo": "documental", "es_obligatorio": True,
                "valor_minimo": None, "documentos_requeridos": [],
            })
            st.rerun()

    with tab_cal:
        for i, c in enumerate(st.session_state.edited_criteria_cal):
            with st.expander(
                f"[{c.get('id','C?')}] {c.get('nombre','Sin nombre')} — {c.get('puntaje_maximo',0)} pts",
                expanded=False,
            ):
                c1, c2 = st.columns(2)
                with c1:
                    nid   = st.text_input("ID",     value=c.get("id",""),     key=f"cal_id_{i}")
                    nnomb = st.text_input("Nombre", value=c.get("nombre",""), key=f"cal_nombre_{i}")
                    npts  = st.number_input("Puntaje máximo",
                                            value=float(c.get("puntaje_maximo",0) or 0),
                                            min_value=0.0, step=1.0, key=f"cal_pts_{i}")
                with c2:
                    ndesc    = st.text_area("Descripción", value=c.get("descripcion","") or "",
                                            key=f"cal_desc_{i}", height=100)
                    nformula = st.text_input("Fórmula (opcional)",
                                             value=str(c.get("formula","") or ""),
                                             key=f"cal_formula_{i}")
                cs, cd = st.columns(2)
                with cs:
                    if st.button("Guardar cambios", key=f"cal_save_{i}"):
                        st.session_state.edited_criteria_cal[i] = {
                            **c, "id": nid, "nombre": nnomb, "descripcion": ndesc,
                            "puntaje_maximo": int(npts), "formula": nformula or None,
                        }
                        st.success("Criterio actualizado")
                        st.rerun()
                with cd:
                    if st.button("Eliminar criterio", key=f"cal_del_{i}"):
                        st.session_state.edited_criteria_cal.pop(i)
                        st.rerun()

        if st.button("+ Agregar criterio de calificación", key="cal_add"):
            n = len(st.session_state.edited_criteria_cal) + 1
            st.session_state.edited_criteria_cal.append({
                "id": f"C{n}", "nombre": "Nuevo criterio", "descripcion": "",
                "puntaje_maximo": 10, "formula": None, "notas": "",
            })
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Propuestas
# ─────────────────────────────────────────────────────────────────────────────
def page_propuestas():
    st.markdown("<div class='section-header'>Propuestas de Empresas</div>", unsafe_allow_html=True)

    # ── Gestión de empresas ───────────────────────────────────────────────────
    col_mgmt1, col_mgmt2 = st.columns([3, 1])
    with col_mgmt1:
        st.markdown("**Gestionar empresas**")
    with col_mgmt2:
        if st.button("+ Agregar empresa"):
            n = len(st.session_state.companies) + 1
            new_name = f"Empresa {n}"
            while new_name in st.session_state.companies:
                n += 1
                new_name = f"Empresa {n}"
            st.session_state.companies.append(new_name)
            _ensure_company_id(new_name)
            st.session_state.active_company = new_name
            st.rerun()

    # ── Tabs de selección de empresa ─────────────────────────────────────────
    companies = st.session_state.companies
    if len(companies) > 1:
        cols = st.columns(len(companies))
        for i, company in enumerate(companies):
            with cols[i]:
                if st.button(company, key=f"tab_{company}", use_container_width=True):
                    st.session_state.active_company = company
                    st.rerun()
    else:
        st.session_state.active_company = companies[0]

    active    = st.session_state.active_company
    active_id = _ensure_company_id(active)

    st.markdown("---")

    # ── Layout: upload | resultado ────────────────────────────────────────────
    col_upload, col_result = st.columns([1, 1], gap="large")

    # ── Columna izquierda: datos y archivos de la empresa ─────────────────────
    with col_upload:
        # Nombre editable
        new_name = st.text_input("Nombre de la empresa", value=active, key=f"name_input_{active_id}")
        if new_name != active and new_name.strip():
            _rename_company(active, new_name)
            st.rerun()

        st.markdown("#### Subir archivos de propuesta")

        # Un único file_uploader por empresa (key = active_id, nunca duplicada)
        uploaded = st.file_uploader(
            f"Selecciona archivos PDF o DOCX para {active}",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            key=f"uploader_{active_id}",
        )

        # Guardar nuevos archivos como bytes (persisten entre pestañas)
        if uploaded:
            current        = st.session_state.company_files.get(active_id, [])
            existing_names = {f["name"] for f in current}
            added          = False
            for f in uploaded:
                if f.name not in existing_names:
                    f.seek(0)
                    current.append({"name": f.name, "bytes": f.read()})
                    existing_names.add(f.name)
                    added = True
            if added:
                st.session_state.company_files[active_id] = current

        # Mostrar archivos guardados con opción de eliminar
        saved_files = st.session_state.company_files.get(active_id, [])
        if saved_files:
            st.markdown("**Archivos guardados:**")
            for i, fd in enumerate(saved_files):
                c1, c2 = st.columns([8, 1])
                with c1:
                    st.markdown(f"✅ `{fd['name']}` ({len(fd['bytes'])/1024:.1f} KB)")
                with c2:
                    if st.button("❌", key=f"del_{active_id}_{i}", help="Eliminar"):
                        st.session_state.company_files[active_id].pop(i)
                        st.rerun()

    # ── Columna derecha: resultado de evaluación ──────────────────────────────
    with col_result:
        st.markdown("#### Resultado de evaluación")
        result = st.session_state.pipeline_results.get(active_id)

        if result and not result.get("error"):
            for p in result.get("scored", []):
                pct   = p.get("porcentaje", 0)
                color = color_for_pct(pct)
                hab   = p.get("habilitado", False)
                st.markdown(f"""
                <div class='card'>
                  <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <div style='font-weight:700;color:#1A1A2E;font-size:15px;'>{p['provider'][:40]}</div>
                    <span class='{"pill-green" if hab else "pill-red"}'>
                      {'HABILITADO' if hab else 'NO HABILITADO'}
                    </span>
                  </div>
                  <div style='margin-top:12px;'>
                    <div style='font-size:13px;color:#64748b;margin-bottom:4px;'>
                      Puntaje total:
                      <b style='color:#1A1A2E;'>{p['puntaje_total']} / {p['puntaje_maximo_posible']} pts</b>
                    </div>
                """, unsafe_allow_html=True)
                render_progress_bar(pct, color)
                st.markdown("</div>", unsafe_allow_html=True)

                comentario = result.get("recommendation", {}).get("justificacion", "")
                if comentario:
                    st.markdown(f"<div class='comment-box'>{comentario}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                with st.expander("Ver desglose de criterios"):
                    criterios_cal = (
                        st.session_state.edited_criteria_cal
                        or st.session_state.rfp_criteria.get("criterios_calificacion", [])
                    )
                    desc_lookup = {c.get("id"): c.get("descripcion", "") for c in criterios_cal}
                    for d in p.get("desglose_puntaje", []):
                        pts     = d.get("puntaje_obtenido", 0)
                        max_pts = d.get("puntaje_maximo", 0)
                        c2      = color_for_pct((pts / max_pts * 100) if max_pts else 0)
                        st.markdown(f"**{d.get('id','')} — {d.get('nombre','')}**")
                        desc = desc_lookup.get(d.get("id"), "")
                        if desc:
                            st.markdown(f"<div class='desc-box'>{desc}</div>", unsafe_allow_html=True)
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            render_progress_bar((pts / max_pts * 100) if max_pts else 0, c2)
                        with col2:
                            st.markdown(f"**{pts:.1f}** / {max_pts} pts")
                        if d.get("evidencia"):
                            st.markdown(f"<div class='evidence-box'>{d['evidencia']}</div>",
                                        unsafe_allow_html=True)

        elif result and result.get("error"):
            st.error(f"Error en la evaluación: {result['error']}")
        else:
            st.markdown("""
            <div class='card' style='border:2px dashed #e2e8f0;text-align:center;padding:40px 20px;color:#94a3b8;'>
              <div style='font-weight:600;'>Pendiente de evaluación</div>
              <div style='font-size:13px;margin-top:4px;'>Ejecuta la evaluación desde el botón inferior</div>
            </div>""", unsafe_allow_html=True)

    # ── Botón de evaluación (fuera de las columnas, ocupa todo el ancho) ──────
    st.markdown("---")
    col_btn, col_status = st.columns([1, 2])

    with col_btn:
        rfp_ready   = st.session_state.rfp_bytes is not None
        files_ready = len(st.session_state.company_files.get(active_id, [])) > 0

        if not rfp_ready:
            st.warning("Primero sube el RFP en la pestaña **RFP y Criterios**")
        elif not files_ready:
            st.warning("Sube al menos un archivo de propuesta")
        else:
            if st.button(f"▶ Evaluar propuesta de {active}", type="primary", use_container_width=True):
                with st.spinner(f"Evaluando {active}… esto puede tardar 1-3 minutos"):
                    # Convertir archivos guardados a objetos tipo-archivo
                    file_objs = [
                        _make_file_like(fd)
                        for fd in st.session_state.company_files.get(active_id, [])
                    ]
                    result = run_pipeline_for(
                        rfp_bytes      = st.session_state.rfp_bytes,
                        rfp_name       = st.session_state.rfp_name,
                        company_name   = active,
                        proposal_files = file_objs,
                    )
                    # Guardar bajo ID interno — sobrevive a renombrados
                    st.session_state.pipeline_results[active_id] = result

                    if result.get("rfp_data") and not st.session_state.criteria_loaded_from_rfp:
                        st.session_state.rfp_criteria        = result["rfp_data"]
                        st.session_state.edited_criteria_hab = list(
                            result["rfp_data"].get("criterios_habilitantes", []))
                        st.session_state.edited_criteria_cal = list(
                            result["rfp_data"].get("criterios_calificacion", []))
                        st.session_state.criteria_loaded_from_rfp = True

                    if result.get("error"):
                        st.error(f"Error: {result['error']}")
                    else:
                        st.success("¡Evaluación completada!")
                    st.rerun()

    with col_status:
        result = st.session_state.pipeline_results.get(active_id)
        if result and not result.get("error") and result.get("report_bytes"):
            st.download_button(
                "⬇ Descargar reporte Word",
                data              = result["report_bytes"],
                file_name         = result.get("report_name", "reporte.docx"),
                mime              = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Resultados Globales
# ─────────────────────────────────────────────────────────────────────────────
def page_resultados():
    st.markdown("<div class='section-header'>Resultados Globales — Ranking de Propuestas</div>",
                unsafe_allow_html=True)

    # Construir resultados usando IDs internos (robustos ante renombrados)
    all_results = {}
    for company in st.session_state.companies:
        cid = _get_company_id(company)
        r   = st.session_state.pipeline_results.get(cid)
        if r and not r.get("error"):
            all_results[company] = r

    if not all_results:
        st.markdown("""
        <div class='card' style='text-align:center;padding:60px 20px;border:2px dashed #e2e8f0;'>
          <div style='font-size:1.2rem;font-weight:700;color:#1e293b;margin-top:12px;'>Sin resultados aún</div>
          <div style='color:#64748b;margin-top:6px;'>Evalúa al menos una empresa para ver el ranking global</div>
        </div>""", unsafe_allow_html=True)
        return

    all_scored = []
    for company, result in all_results.items():
        for p in result.get("scored", []):
            all_scored.append({**p, "_empresa": company})
    all_scored.sort(key=lambda x: (x.get("habilitado", False), x.get("puntaje_total", 0)), reverse=True)

    total       = len(all_scored)
    habilitados = sum(1 for p in all_scored if p.get("habilitado"))
    mejor       = all_scored[0] if all_scored else None

    mc1, mc2, mc3, mc4 = st.columns(4)
    for col, (label, value, color) in zip(
        [mc1, mc2, mc3, mc4],
        [
            ("Total evaluadas",  total,              "#E63946"),
            ("Habilitadas",      habilitados,         "#22c55e"),
            ("No habilitadas",   total-habilitados,   "#ef4444"),
            ("Mejor puntaje",    f"{mejor['puntaje_total']:.1f}" if mejor else "—", "#f59e0b"),
        ],
    ):
        with col:
            st.markdown(f"""
            <div style='background:{color};border-radius:12px;padding:20px;text-align:center;color:white;'>
              <div style='font-size:2rem;font-weight:700;'>{value}</div>
              <div style='font-size:12px;opacity:0.9;margin-top:4px;'>{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Ranking completo")
    st.markdown("""
    <div style='display:grid;grid-template-columns:50px 1fr 160px 180px 130px;gap:8px;
                padding:10px 12px;background:#f8fafc;border-radius:8px;
                font-size:12px;font-weight:700;color:#64748b;
                text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;'>
      <div>#</div><div>Empresa / Propuesta</div><div>Puntaje</div><div>Precio</div><div>Estado</div>
    </div>""", unsafe_allow_html=True)

    rank_counter = 1
    for p in all_scored:
        hab        = p.get("habilitado", False)
        precio     = p.get("precio_ofertado")
        moneda     = p.get("calificacion_detalle", {}).get("propuesta_economica_detalle", {}).get("moneda", "")
        precio_str = format_currency(precio, moneda) if precio else "N/D"
        puntaje    = p.get("puntaje_total", 0)
        max_pts    = p.get("puntaje_maximo_posible", 100)

        if hab:
            rank_label = str(rank_counter)
            rank_class = f"rank-{min(rank_counter, 3)}" if rank_counter <= 3 else "rank-n"
            rank_counter += 1
        else:
            rank_label = "—"
            rank_class = "rank-n"

        st.markdown(f"""
        <div style='display:grid;grid-template-columns:50px 1fr 160px 180px 130px;gap:8px;
                    align-items:center;padding:14px 12px;background:white;
                    border:1px solid #e2e8f0;border-radius:10px;margin-bottom:6px;'>
          <div><span class='rank-badge {rank_class}'>{rank_label}</span></div>
          <div>
            <div style='font-weight:600;color:#1A1A2E;font-size:14px;'>{p['provider'][:45]}</div>
            <div style='font-size:12px;color:#94a3b8;margin-top:2px;'>{p.get("_empresa","")}</div>
          </div>
          <div style='font-weight:700;color:#E63946;font-size:16px;'>{puntaje:.1f} / {max_pts}</div>
          <div style='font-size:13px;color:#475569;'>{precio_str}</div>
          <div><span class='{"pill-green" if hab else "pill-red"}'>
            {"HABILITADO" if hab else "NO HAB."}
          </span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Recomendación de la IA")
    all_recs = [r.get("recommendation", {}) for r in all_results.values() if r.get("recommendation")]

    if all_recs:
        ganador = next((r.get("ganador_sugerido") for r in all_recs if r.get("ganador_sugerido")), None)
        if ganador:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#1A1A2E,#16213E);border-radius:14px;
                        padding:24px 28px;margin-bottom:20px;'>
              <div style='font-size:11px;color:#E63946;font-weight:700;letter-spacing:1.5px;margin-bottom:8px;'>
                PROPUESTA RECOMENDADA
              </div>
              <div style='font-size:1.4rem;font-weight:800;color:#ffffff;'>{ganador}</div>
            </div>""", unsafe_allow_html=True)
        for rec in all_recs:
            if rec.get("justificacion"):
                st.markdown(f"""
                <div class='card' style='border-left:4px solid #E63946;'>
                  <div style='font-size:12px;color:#E63946;font-weight:700;margin-bottom:8px;'>JUSTIFICACIÓN</div>
                  <div style='color:#1e293b;line-height:1.6;'>{rec['justificacion']}</div>
                </div>""", unsafe_allow_html=True)
            if rec.get("analisis_comparativo"):
                st.markdown(f"""
                <div class='card' style='border-left:4px solid #0F3460;'>
                  <div style='font-size:12px;color:#0F3460;font-weight:700;margin-bottom:8px;'>ANÁLISIS COMPARATIVO</div>
                  <div style='color:#1e293b;line-height:1.6;'>{rec['analisis_comparativo']}</div>
                </div>""", unsafe_allow_html=True)
            for a in rec.get("alertas", []):
                st.warning(a)
            if rec.get("recomendacion_final"):
                st.info(f"Recomendación ejecutiva: {rec['recomendacion_final']}")
    else:
        st.markdown("<div style='color:#64748b;'>No se han generado recomendaciones aún.</div>",
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Descargar reportes")
    for company, result in all_results.items():
        if result.get("report_bytes"):
            cid = _get_company_id(company)
            st.download_button(
                f"⬇ Reporte de {company}",
                data      = result["report_bytes"],
                file_name = result.get("report_name", f"reporte_{company}.docx"),
                mime      = "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key       = f"dl_{cid}",
            )


# ─────────────────────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────────────────────
page = st.session_state.page
if page == "RFP":
    page_rfp()
elif page == "Propuestas":
    page_propuestas()
elif page == "Resultados":
    page_resultados()