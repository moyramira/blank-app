import streamlit as st
import pandas as pd
import re
from io import BytesIO

def process_txt(file):
    lines = file.getvalue().decode("utf-8").splitlines()
    data = []

    for line in lines:
        if line.startswith("4"):
            cpf_match = re.search(r"\d{11}[MF]", line)
            if cpf_match:
                cpf_start = cpf_match.start()
                cpf = line[cpf_start:cpf_start+11]

                name_start = 43
                name_end = cpf_start
                name_raw = line[name_start:name_end].strip()
                name_clean = re.sub(r"[^A-Za-zÀ-ÿ\s]", "", name_raw).strip()

                value_match = re.search(r"\d{7}$", line.strip())
                if value_match:
                    value = int(value_match.group()) / 100
                    formatted_value = f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    data.append((name_clean, cpf, formatted_value))

    df = pd.DataFrame(data, columns=["Nome do Beneficiário", "CPF", "Valor Final (R$)"])
    return df

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Beneficiários')
    return output.getvalue()

# Interface do Streamlit
st.title("📄 Conversão TXT Pluxee")

uploaded_file = st.file_uploader("Envie o arquivo .txt", type="txt")

if uploaded_file:
    df = process_txt(uploaded_file)
    st.success("Arquivo processado com sucesso!")
    st.dataframe(df)

    excel_data = to_excel(df)
    st.download_button(
        label="📥 Baixar Excel",
        data=excel_data,
        file_name="beneficiarios_limpo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.info("Se o download não iniciar automaticamente, clique no botão acima.")
