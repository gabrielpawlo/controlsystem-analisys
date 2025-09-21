import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import control as ct
from tkinter import messagebox


class AnalisadorSistema:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador de Sistema")
        self.root.geometry("1100x650")

        # Estilo (tema bootstrap)
        style = tb.Style("cosmo")

        # Frames
        left_frame = tb.Frame(root, padding=15)
        left_frame.pack(side=LEFT, fill=Y)

        right_frame = tb.Frame(root)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # Inputs Planta
        tb.Label(left_frame, text="Planta - Numerador:").pack(anchor="w")
        self.entry_num_planta = tb.Entry(left_frame, bootstyle="info")
        self.entry_num_planta.pack(fill="x", pady=2)

        tb.Label(left_frame, text="Planta - Denominador:").pack(anchor="w")
        self.entry_den_planta = tb.Entry(left_frame, bootstyle="info")
        self.entry_den_planta.pack(fill="x", pady=2)

        # Inputs Controlador
        tb.Label(left_frame, text="Controlador - Numerador:").pack(anchor="w", pady=(10, 0))
        self.entry_num_ctrl = tb.Entry(left_frame, bootstyle="success")
        self.entry_num_ctrl.pack(fill="x", pady=2)

        tb.Label(left_frame, text="Controlador - Denominador:").pack(anchor="w")
        self.entry_den_ctrl = tb.Entry(left_frame, bootstyle="success")
        self.entry_den_ctrl.pack(fill="x", pady=2)

        # Botões
        tb.Button(left_frame, text="📈 Plotar", bootstyle="primary outline", command=self.plotar).pack(pady=5, fill="x")
        tb.Button(left_frame, text="❌ Sair", bootstyle="danger outline", command=root.quit).pack(pady=5, fill="x")

        # Informações
        self.labels = {}
        info_frame = tb.Labelframe(left_frame, text="📊 Informações", padding=10, bootstyle="info")
        info_frame.pack(fill="both", expand=True, pady=10)

        infos = ["Tempo de Subida", "Sobressinal", "Pico", "Tempo do Pico",
                 "Tempo de acomodação", "Estado estável", "Quantidade de Polos", "Quantidade de Zeros"]

        for key in infos:
            frame = tb.Frame(info_frame)
            frame.pack(fill="x", pady=3)
            tb.Label(frame, text=key + ": ").pack(side="left")
            lbl = tb.Label(frame, text="---", bootstyle="secondary")
            lbl.pack(side="right")
            self.labels[key] = lbl

        # Gráfico matplotlib
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.plot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=1)

    def plotar(self):
        try:
            numerator = list(map(float, self.entry_num_planta.get().split()))
            denominator = list(map(float, self.entry_den_planta.get().split()))
            sistema = ct.tf(numerator, denominator)

            num_ctrl = list(map(float, self.entry_num_ctrl.get().split()))
            den_ctrl = list(map(float, self.entry_den_ctrl.get().split()))
            controlador = ct.tf(num_ctrl, den_ctrl)

            malha_aberta = ct.series(controlador, sistema)
            sis_final = ct.feedback(malha_aberta, 1)

            time, response = ct.step_response(sis_final)
            resposta = ct.step_info(sis_final)

            # Atualiza métricas
            self.labels["Tempo de Subida"].config(text=round(resposta['RiseTime'], 3))
            self.labels["Sobressinal"].config(text=round(resposta['Overshoot'], 3))
            self.labels["Pico"].config(text=round(resposta['Peak'], 3))
            self.labels["Tempo do Pico"].config(text=round(resposta['PeakTime'], 3))
            self.labels["Tempo de acomodação"].config(text=round(resposta['SettlingTime'], 3))
            self.labels["Estado estável"].config(text=round(resposta['SteadyStateValue'], 3))

            polos = ct.poles(sis_final)
            zeros = ct.zeros(sis_final)
            self.labels["Quantidade de Polos"].config(text=len(polos))
            self.labels["Quantidade de Zeros"].config(text=len(zeros))

            # Atualiza gráfico
            self.ax.clear()
            self.ax.grid(True, linestyle="--", alpha=0.7)
            self.ax.plot(time, response, color="blue", linewidth=2)
            self.ax.set_title("Resposta ao Degrau", fontsize=12, fontweight="bold")
            self.ax.set_xlabel("Tempo")
            self.ax.set_ylabel("Amplitude")
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar: {e}")


if __name__ == "__main__":
    root = tb.Window(themename="cosmo")  # pode trocar: cosmo, darkly, cyborg, journal...
    app = AnalisadorSistema(root)
    root.mainloop()
