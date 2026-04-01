import streamlit as st
import pandas as pd
import numpy as np
import io
from PIL import Image
from io import BytesIO
import base64


# Configurações da página

st.set_page_config(
    page_title="Formulário PD",
    page_icon="🧾",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Leitura dos dados

dados = pd.read_excel(
    "experimento_rev02.xlsx", sheet_name="Codificação", skiprows=1, engine="openpyxl"
)
variaveis = dados.columns[1:9]
colunas = list(dados.columns)
colunas[1:] = variaveis
dados.columns = colunas
niveis = pd.read_excel("experimento_rev02.xlsx", sheet_name="Níveis")
niveis["Variável"] = niveis["Variável"].ffill()

niveis["Nível"] = niveis["Nível"].astype(str)
niveis = niveis[["Variável", "Código", "Nível", "Tipo"]]

# Formulário PD

st.title("Formulário para Pesquisa de Preferência Declarada")

st.markdown("Se o entrevistado tiver 20 minutos, edite os níveis abaixo para refletir a realidade da empresa dele. Caso contrário, deixe os níveis como estão e avance para o formulário.")

editar = st.radio("Deseja editar os níveis?", ["Não", "Sim"], horizontal=True)
if editar == "Sim":
    niveis = st.data_editor(
        niveis,
        disabled=["Variável", "Código", "Cor"],
        key="editor_niveis",
    )


nome = st.text_input("Nome da empresa (*)", key="nome")

nome_entrevistado = st.text_input("Nome do entrevistado (*)", key="nome_entrevistado")

st.header(
    "Em relação ao principal produto expedido pela empresa (o com maior movimentação anual em peso), responda as seguintes questões:"
)


produto = st.text_input("1 - Qual o produto com maior movimentação anual em peso? (*)", key="produto")

modos_opcoes = [
    "Rodoviário",
    "Aeroviário",
    "Ferroviário",
    "Cabotagem",
    "Hidroviário",
    "Dutoviário",
]

modos_baixa_opcoes = [
    "Rodoviário",
    "Aeroviário",
]

modos_alta_opcoes = [
    "Ferroviário",
    "Cabotagem",
    "Hidroviário",
    "Dutoviário",
]

modos_opcoes_img = {
    "Rodoviário": "imgs/truck.png",
    "Ferroviário": "imgs/train.png",
    "Cabotagem": "imgs/ship.png",
    "Hidroviário": "imgs/boat.png",
    "Aeroviário": "imgs/plane.png",
    "Dutoviário": "imgs/pipe.png",
}

#modos_utilizados = st.selectbox(
#    "2 - Qual o modo de baixa capacidade utilizado? (*)",
#    modos_baixa_opcoes,
#    key="modos_utilizados",
#)

modos_utilizados = ["Rodoviário"]

# Modos propostos para os cartões B
#modos_propostos = st.selectbox(
#    "3 - Qual o modo de alta capacidade que poderia ser utilizado alternativamente? (*)",
#    modos_alta_opcoes,
#    key="modos_propostos",
#)

modos_propostos = ["Ferroviário"]

modos_filtrados = [modo for modo in modos_opcoes if modo not in modos_utilizados]

#modos_nao_usaria = st.multiselect(
#    "4 - Existe algum modo que você não usaria para fazer o transporte desse produto, independentemente de tempo, custo, confiabilidade, flexibilidade e segurança? Se sim, por quê?",
#    modos_filtrados + ["Outro"],
#    key="modos_nao_usaria",
#)

#nao_usaria_outro = ""
#if "Outro" in modos_nao_usaria:
#    nao_usaria_outro = st.text_input(
#        "4.1 - Qual outro modo você não usaria?", key="nao_usaria_outro"
#    )

#motivo_nao_usaria = ""
#if len(modos_nao_usaria) > 0:
#    motivo_nao_usaria = st.text_area(
#        "4.2 - Por que você não usaria esse(s) modo(s)?", key="motivo_nao_usaria"
#    )

origem = st.text_input(
    "2 - Quanto à principal rota de movimentação deste produto, qual a ORIGEM da rota? (Escrever Município e Estado. Caso carga de importação, escrever o nome do porto de entrada no Brasil).  (*)",
    key="origem",
)

destino = st.text_input(
    "3 - Quanto à principal rota de movimentação deste produto, qual a DESTINO da rota? (Escrever Município e Estado. Caso carga de importação, escrever o nome do porto de entrada no Brasil).  (*)",
    key="destino",
)


custo = st.number_input(
    "4 - Qual é o valor de frete unitário de transporte do produto nesta rota, em R$/tonelada?  (*)",
    min_value=0.00,
    step=0.01,
    key="custo_atual",
)

st.write("5 - Qual o tempo de deslocamento dessa carga nessa rota? (*)")

col1, col2, col3 = st.columns([1, 1, 1])  # três colunas lado a lado

with col1:
    dia = st.number_input("Dias", min_value=0, max_value=99999999, value=0)

with col2:
    hora = st.number_input("Horas", min_value=0, max_value=99999999, value=0)

with col3:
    minuto = st.number_input("Minutos", min_value=0, max_value=99999999, value=0)

tempo = dia * 24 * 60 + hora * 60 + minuto


modos_utilizados_img = [
    modos_opcoes_img[modo] for modo in modos_utilizados if modo in modos_opcoes_img
]
modos_propostos_img = [
    modos_opcoes_img[modo] for modo in modos_propostos if modo in modos_opcoes_img
]


st.markdown("**Campos com (*) são obrigatórios.**")


st.text(
    "A seguir serão mostrados cenários hipotéticos de escolha de modo/rota e gostaria que o(a) sr.(a) informasse se escolheria a situação de transporte da opção A ou da opção B para transportar esse produto considerando custo, tempo, confiabilidade, segurança e capacidade."
)

# Cartões
batch_list = [[1, 2, 3, 4, 5, 6, 7, 8, 9], [10, 11, 12, 13, 14, 15, 16, 17, 18]]

# Verificar campos obrigatórios
campos_ok = all(
    [
        nome != "",
        produto != "",
        modos_utilizados is not None,
        modos_propostos is not None,
        custo != 0.0,
        tempo > 0,
    ]
)

# PD
if "cartao_atual" not in st.session_state:
    st.session_state.cartao_atual = 0

if "respostas" not in st.session_state:
    st.session_state.respostas = {}

i = st.session_state.cartao_atual

if "iniciado" not in st.session_state:
    st.session_state.iniciado = False

if not st.session_state.iniciado:
    if st.button("Iniciar experimento", type="secondary", use_container_width=True):
        if not campos_ok:
            st.warning(
                "Preencha todas as perguntas obrigatórias antes de iniciar o experimento."
            )
            st.session_state.iniciado = False
        else:
            st.session_state.iniciado = True
            st.rerun()

if st.session_state.iniciado:
    if "cartoes_embaralhados" not in st.session_state:
        options = [np.random.permutation(list) for list in batch_list]
        options = [int(x) for sublist in options for x in sublist]
        st.session_state.cartoes_embaralhados = options
    cartoes = st.session_state.cartoes_embaralhados
    if i < len(cartoes):
        cartao = cartoes[i]
        st.markdown(f"## Cartão {cartao}")

        option_i_data = dados.loc[dados["Cartão"] == cartao].copy()

        option_i_data = option_i_data.melt(
            id_vars="Cartão", value_name="Código", var_name="Variável"
        )
        option_i_data = option_i_data.merge(
            niveis, on=["Variável", "Código"], how="left"
        )

        option_i_data["valores"] = option_i_data["Nível"]

        def ajustar_valores(row, custo, tempo):
            if row["Variável"] in ["Custo A", "Custo B", "Tempo A", "Tempo B"]:
                row["valores"] = float(row["valores"])
                row["valores"] += 1
            if row["Variável"] in ["Custo A", "Custo B"]:
                row["valores"] *= custo
            elif row["Variável"] in ["Tempo A", "Tempo B"]:
                row["valores"] *= tempo

            if row["Variável"] in ["Modo B"]:
                if cartao > 9:
                    row["valores"] = ", ".join(modos_utilizados)
                else:
                    row["valores"] = ", ".join(modos_propostos)
            return row

        option_i_data = option_i_data.apply(
            ajustar_valores, axis=1, custo=custo, tempo=tempo
        )

        option_i_data["option"] = option_i_data["Variável"].apply(
            lambda x: x.split()[-1]
        )
        option_i_data["Variável"] = option_i_data["Variável"].apply(
            lambda x: x.split()[0]
        )

        def formatar_nivel(row):
            if row["Variável"] == "Custo":
                row["Nível"] = float(row["Nível"])
                return (
                    f"R$ {row['valores']:.2f} (Variação de {row['Nível']:.0%})".replace(
                        ".", ","
                    )
                )
            elif row["Variável"] == "Tempo":
                row["Nível"] = float(row["Nível"])
                dias = int(row["valores"] // 1440)
                resto = row["valores"] % 1440
                horas = int(resto // 60)
                minutos = int(resto % 60)
                return f"{dias} dias, {horas} hora(s) e {minutos} min (Variação de {row['Nível']:.0%})"
            return row["valores"]

        option_i_data["valores"] = option_i_data.apply(formatar_nivel, axis=1)

        df_pivot = option_i_data.pivot(
            index="Variável", columns="option", values="valores"
        )

        df_pivot_tipo = option_i_data.pivot(
            index="Variável", columns="option", values="Tipo"
        )

        df_pivot.fillna("como é atualmente", inplace=True)

        df_pivot_tipo.fillna("igual", inplace=True)

        ordem_var = [
            "Modo",
            "Tempo",
            "Custo",
            "Confiabilidade",
            "Segurança",
            "Capacidade",
        ]
        df_pivot.index = pd.Categorical(
            df_pivot.index, categories=ordem_var, ordered=True
        )
        df_pivot = df_pivot.sort_index()

        df_pivot_tipo.index = pd.Categorical(
            df_pivot_tipo.index, categories=ordem_var, ordered=True
        )
        df_pivot_tipo = df_pivot_tipo.sort_index()

        map_index = {
            "Modo": "Modo",
            "Tempo": "Tempo de Viagem",
            "Custo": "Custo de Envio",
            "Confiabilidade": "Confiabilidade",
            "Segurança": "Segurança",
            "Capacidade": "Capacidade",
        }

        df_pivot.index = df_pivot.index.map(map_index)

        df_pivot_tipo.index = df_pivot_tipo.index.map(map_index)

        df_pivot.loc["Modo", "A"] = ", ".join(modos_utilizados)

        col1, col2 = st.columns(2)

        def image_to_base64(img):
            if img:
                with BytesIO() as buffer:
                    img.save(buffer, "PNG")
                    raw_base64 = base64.b64encode(buffer.getvalue()).decode()
                return f"data:image/png;base64,{raw_base64}"

        def get_image(url):
            img = Image.open(url)
            return image_to_base64(img)

        with col1:
            conteudo_a = """
            <div style='border: 2px solid #D3D3D3; border-radius: 10px; padding: 15px; display: flex; gap: 15px; align-items: flex-start;'>
                <div>
                    <h4 style='margin-top: 0;'>Opção A</h4>
            """

            for (idx, val), (_, tipo) in zip(
                df_pivot["A"].items(), df_pivot_tipo["A"].items()
            ):
                if tipo == "igual":
                    conteudo_a += f"<p><strong>{idx}:</strong> {val}</p>"

                elif tipo == "melhor":
                    conteudo_a += (
                        f"<p><strong>{idx}:</strong> "
                        f"<span style='color:#5FA8D3'>{val}</span></p>"
                    )
                else:
                    conteudo_a += (
                        f"<p><strong>{idx}:</strong> "
                        f"<span style='color:red'>{val}</span></p>"
                    )

            conteudo_a += (
                "</div><div style='display: flex; flex-direction: column; gap: 5px;'>"
            )

            for img in modos_utilizados_img:
                conteudo_a += f"<img src='{get_image(img)}' width='60' style='border-radius: 8px; background-color: white;'>"

            conteudo_a += "</div></div>"
            st.markdown(conteudo_a, unsafe_allow_html=True)

        with col2:
            conteudo_b = """
            <div style='border: 2px solid #D3D3D3; border-radius: 10px; padding: 15px; display: flex; gap: 15px; align-items: flex-start;'>
                <div>
                    <h4 style='margin-top: 0;'>Opção B</h4>
            """

            for (idx, val), (_, tipo) in zip(
                df_pivot["B"].items(), df_pivot_tipo["B"].items()
            ):
                if tipo == "igual":
                    conteudo_b += f"<p><strong>{idx}:</strong> {val}</p>"

                elif tipo == "melhor":
                    conteudo_b += (
                        f"<p><strong>{idx}:</strong> "
                        f"<span style='color:#5FA8D3'>{val}</span></p>"
                    )
                else:
                    conteudo_b += (
                        f"<p><strong>{idx}:</strong> "
                        f"<span style='color:red'>{val}</span></p>"
                    )

            conteudo_b += (
                "</div><div style='display: flex; flex-direction: column; gap: 5px;'>"
            )

            if cartao > 9:
                for img in modos_utilizados_img:
                    conteudo_b += f"<img src='{get_image(img)}' width='60' style='border-radius: 8px; background-color: white;'>"
            else:
                for img in modos_propostos_img:
                    conteudo_b += f"<img src='{get_image(img)}' width='60' style='border-radius: 8px; background-color: white;'>"

            conteudo_b += "</div></div>"

            st.markdown(conteudo_b, unsafe_allow_html=True)

        opcoes = ["Selecione uma opção", "A", "B", "Não responder"]

        escolha = st.radio(
            "Qual opção você prefere?", options=opcoes, key=f"cartao_{cartao}"
        )

        if escolha != "Selecione uma opção" and escolha != "Não responder":
            st.write(f"Você escolheu: {escolha}")
            if st.button("Próximo", type="secondary", use_container_width=True):
                st.session_state.respostas[cartao] = escolha
                st.session_state.cartao_atual += 1
                st.rerun()
        elif escolha == "Não responder":
            st.write("Você escolheu: Não responder")
            if st.button("Próximo", type="secondary", use_container_width=True):
                st.session_state.respostas[cartao] = "Não respondeu"
                st.session_state.cartao_atual += 1
                st.rerun()
        else:
            st.write("Por favor, selecione uma opção.")

    else:
        df_resultado = (
            pd.DataFrame.from_dict(
                st.session_state.respostas, orient="index", columns=["Escolha"]
            )
            .reset_index()
            .rename(columns={"index": "Cartão"})
        )

        # Variáveis para salvar no formulário

        df_resultado.insert(0, "Nome", nome)
        df_resultado.insert(1, "Produto", produto)
        df_resultado.insert(
            2, "Modo de Baixa Capacidade Utilizado", ", ".join(modos_utilizados)
        )
        df_resultado.insert(
            3,
            "Modo de Alta Capacidade Que Poderia Ser Utilizado",
            ", ".join(modos_propostos),
        )
        df_resultado.insert(4, "Modos Não Usaria", ", ".join([]))
        df_resultado.insert(5, "Outro Modo Não Usaria", "")
        df_resultado.insert(6, "Motivo Não Usaria", "")
        df_resultado.insert(7, "Custo Total", custo)
        df_resultado.insert(8, "Tempo de Deslocamento", tempo)
        df_resultado.insert(9, "Conjunto de Cartões", str(cartoes))
        df_resultado.insert(10, "Nome entrevistado", str(nome_entrevistado))
        df_resultado.insert(11, "Origem", str(origem))
        df_resultado.insert(12, "Destino", str(destino))

        st.dataframe(df_resultado)

        st.success(
            "Você completou todos os cartões! Baixe os resultados no botão abaixo."
        )

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_resultado.to_excel(writer, sheet_name="Respostas", index=False)
            niveis.to_excel(writer, sheet_name="Níveis", index=False)

        st.download_button(
            label="📥 Baixar respostas em Excel",
            data=buffer.getvalue(),
            file_name=f"respostas_{nome.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="secondary",
            use_container_width=True,
        )

        if st.button("Nova pesquisa", type="primary", use_container_width=True):
            # Limpar o formulário para uma nova pesquisa
            st.session_state.clear()

            # st.session_state["nome"] = ""
            # st.session_state["produto"] = ""
            # st.session_state["modos_utilizados"] = []
            # st.session_state["modo_outro"] = ""
            # st.session_state["motivo_uso"] = ""
            # st.session_state["modos_nao_usaria"] = []
            # st.session_state["nao_usaria_outro"] = ""
            # st.session_state["motivo_nao_usaria"] = ""
            # st.session_state["custo_atual"] = 0
            # st.session_state["distancia"] = "Até 100"

            st.rerun()


st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; font-size: 0.9rem; color: gray;">
       Formulário para Pesquisa de Preferência Declarada - Consórcio Concremat/Transplan<br>
        <span style="font-size: 0.8rem;">Versão 1.1.0</span>
    </div>
    """,
    unsafe_allow_html=True,
)
