import streamlit as st
import time
import os
import boto3
import requests
import io
import json
import os
from datetime import datetime, timedelta
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(page_title="MeLi Classifier", layout="wide")

s3_bucket = os.environ.get("S3_BUCKET") 
dag_id = os.environ.get("DAG_ID") 
airflow_api_url = os.environ.get("AIRFLOW_API_URL")
airflow_api_user = os.environ.get("AIRFLOW_API_USER")
airflow_api_password = os.environ.get("AIRFLOW_API_PASS")



def read_s3_file(product_id, s3_bucket, show_message=True):
    """
    Tenta carregar o ARQUIVO JSON com os resultados JÁ PROCESSADOS do S3.
    """
    session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name="us-east-1"
    )
    s3_client = session.client("s3")

    key = f"reviews_mercadolivre/{product_id}/processed/results.json"
    
    print_message(message=f"Tentando carregar arquivo de comentários no S3.", background_color='#FFF3CD') 
            
    file_content=None

    objects = s3_client.list_objects_v2(Bucket=s3_bucket).get('Contents', [])
    for content in objects:
        if content['Key'] == key:
            last_modified=content['LastModified']
            current_date = datetime.now()
            past_thirty_days = current_date - timedelta(days=30)

            if last_modified.date() < past_thirty_days.date():
                if show_message:
                    print_message(
                        message="Arquivo encontrado, mas está desatualizado (mais de 30 dias). Nova análise será executada.",
                        background_color="#FFC4C4"
                    )
                return None

            else:
                response = s3_client.get_object(Bucket=s3_bucket, Key=content['Key'])
                buffer = io.BytesIO(response['Body'].read())
                file_content = json.loads(buffer.getvalue().decode('utf-8'))

                print_message(
                    message="Arquivo encontrado e carregado com sucesso.",
                    background_color='#B6CEB4'
                )
                return file_content

    if show_message:
        print_message(
            message="Arquivo não encontrado no S3. Disparando DAG para busca dos comentários.",
            background_color='#FFC4C4'
        )
    return None





def trigger_airflow_dag(product_id, airflow_api_password, airflow_api_user):
    """
    Dispara a DAG no Airflow usando a API REST.
    Isso diz ao Airflow: "Comece a rodar o pipeline para este product_id".
    """
    dag_run_url = f"{airflow_api_url.rstrip('/')}/api/v1/dags/{dag_id}/dagRuns"

    payload = {"conf": {"product_id": product_id}}
    
    print_message(message=f"Disparando DAG: {dag_run_url} com ID: {product_id}", background_color='#FFF3CD')
    
    try:
        response = requests.post(
            dag_run_url,
            auth=(airflow_api_user, airflow_api_password),
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print_message(message="DAG disparada com sucesso.", background_color='#B6CEB4')
            return True, response.json()
            
    except Exception as e:
        print_message(message=f"Erro ao conectar com o Airflow: {e}", background_color='#FFC4C4')
    



def print_message(message, background_color):

    st.markdown(
    f"""
    <div style="
        background-color: {background_color};
        color: #856404;
        border-left: 5px solid #FFEEA8;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 15px;
        margin-bottom: 20px;">
        ⚠️ {message}
    </div>
    """,
    unsafe_allow_html=True
    )




def display_css():
    """Aplica todo o CSS customizado na página."""
    st.markdown("""
    <style>
        body, .stApp { background-color: #f6f7fb; }
        .block-container { padding-top: 32px; }
        div[data-testid="stForm"]{
          background: #ffffff;
          border-radius: 16px;
          padding: 28px 32px;
          box-shadow: 0 10px 24px rgba(0,0,0,.06);
          border: 1px solid rgba(0,0,0,.05);
        }
        div[data-testid="stTextInput"] input {
          width: 100%;
          height: 40px;
          border-radius: 10px;
          border: 1px solid #F8F7FB;
          padding: 0 10px;
          background-color: #F2F2F2;
          color: #6b7280;
        }
        div[data-testid="stTextInput"] input::placeholder {
          color: #D0D3DC;
          opacity: 1;
        }
        div[data-testid="stFormSubmitButton"] button {
          width: 100%;
          height: 40px;
          border-radius: 8px;
          background-color: #1B8EF2;
          color: white;
          border: none;
          font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)



def display_header_and_form():
    """Mostra o cabeçalho e o formulário de busca."""
    _, center, _ = st.columns([1, 10, 1])
    with center:
        with st.form("header_search"):
            st.markdown(
                "<h1 style='text-align:center; color:#1B8EF2; margin:0;'>Analisador de Feedbacks</h1>"
                "<p style='text-align:center; color:#6b7280; margin-top:1px; margin-bottom:30px; font-size: 18px;'>"
                "Descubra o sentimento das avaliações de qualquer produto do Mercado Livre"
                "</p>",
                unsafe_allow_html=True
            )

            col1, col2 = st.columns([3, 1])
            with col1:
                product_id = st.text_input(
                    "Digite o ID do produto (ex: MLB123456789)",
                    label_visibility="collapsed",
                    placeholder="Digite o ID do produto (ex: MLB123456789)"
                    )
            with col2:
                submit = st.form_submit_button("Analisar 🔎")
    
    return product_id, submit



def display_processing_message(product_id):
    """Mostra a mensagem de "processando" quando um resultado não é encontrado."""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 40px; background: #fff; border-radius: 12px; box-shadow: 0 10px 24px rgba(0,0,0,.06);">
            <h3 style="color: black;">Análise não encontrada para o ID: {product_id}</h3>
            <p style="color: #6b7280;">Solicitando novo processamento. Isso pode levar alguns minutos.</p>
            <p style="color: #6b7280;">Por favor, aguarde, a análise será exibida ao término do processamento.</p>
        </div>
        """, unsafe_allow_html=True
    )




def display_results_dashboard(results, product_id):
    """Pega o dicionário de resultados e mostra o dashboard completo."""
    
    prediction_percent = results['positives_percent']
    product_name = results['product_name']
    negative_comments = results['negatives']
    analysis_confidence = results['confidence']
    total_comments = results['total_comments']

    bar_color = "#16a34a" if prediction_percent >= 50 else "#dc2626" 
    
    st.markdown(f"""
    <div style="text-align:center; margin-top:30px;">
        <h3 style="color:#111827; margin-bottom:5px;">{product_name}</h3>
        <p style="color:#6b7280; margin-top:0;">ID: {product_id}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background:#fff6f6; padding:30px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.05);">
    <div style="display:flex; gap:20px; margin-top:10px; align-items:center;">
        <div style="flex:1; background:white; padding:20px; border-radius:12px; text-align:center;">
            <h2 style="color:#111827;">{total_comments}</h2>
            <p style="color:#6b7280;">Total de Avaliações</p>
        </div>
        <div style="flex:1; background:white; padding:20px; border-radius:12px; text-align:center;">
            <h2 style="color:#111827;">{analysis_confidence:.0f}%</h2>
            <p style="color:#6b7280;">Confiança Média da Análise</p>
        </div>
        <div style="flex:1; background:white; padding:20px; border-radius:12px; text-align:center;">
            <h2 style="color:{bar_color};">{prediction_percent:.0f}%</h2>
            <p style="color:#111827;">Feedbacks {'Positivos' if prediction_percent >= 50 else 'Negativos'}</p>
        </div>
    </div>
    <div style="margin-top:30px; display:flex; justify-content:center;">
        <div style="width:80%; background:#e5e7eb; height:14px; border-radius:10px;">
            <div style="width:{prediction_percent}%; background:{bar_color}; height:100%; border-radius:10px;"></div>
        </div>
    </div>
    <div style="width:80%; margin:auto; display:flex; justify-content:space-between;">
        <p style="margin-top:10px; color:#111827;">Negativo</p>
        <p style="margin-top:10px; color:#111827;">Positivo</p>
    </div>
    </div>
    """, unsafe_allow_html=True)

    if len(negative_comments) != 0:
        st.markdown(
            """
            <div style="margin-top:40px;">
                <h3 style="color:#111827; text-align:center;">Exemplos de Comentários Negativos</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        comments_html = """
        <div style="width:80%; margin:auto; background:#C9E6F2; padding:15px; border-radius:12px; max-height:300px; overflow-y:auto;">
        """
        for comment in negative_comments[:10]: 
            comments_html += f"<p style='margin:5px 0; color:#111827;'>• {comment}</p>"
        comments_html += "</div>"
        
        st.markdown(comments_html, unsafe_allow_html=True)
    else:
        st.write("Nenhum comentário negativo encontrado.")



def main():
    """Função principal que orquestra a aplicação Streamlit."""

    if "show_dashboard" not in st.session_state:
        st.session_state.show_dashboard = False
        st.session_state.final_results = None
        st.session_state.product_id = None

    display_css()
    product_id, submit = display_header_and_form()

    if st.session_state.show_dashboard:
        if st.session_state.final_results:
            display_results_dashboard(
                results=st.session_state.final_results, 
                product_id=st.session_state.product_id
            )
        st.session_state.show_dashboard = False
        st.session_state.final_results = None
        st.session_state.product_id = None
        return 
    

    if submit and product_id:
        placeholder = st.empty() 
        placeholder.markdown(
            """
            <div style="display: flex; justify-content: center; ...">
                <h4 style="color: black;">🔎 Verificando análises existentes...</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        prediction_results = read_s3_file(
            product_id=product_id, 
            s3_bucket=s3_bucket, 
            show_message=True 
        )
        
        placeholder.empty() 

        if prediction_results is not None:
            st.session_state.final_results = prediction_results
            st.session_state.product_id = product_id
            st.session_state.show_dashboard = True
            st.rerun() 

        else:
            display_processing_message(product_id)
            trigger_airflow_dag(
                product_id=product_id,
                airflow_api_password=airflow_api_password,
                airflow_api_user=airflow_api_user
            )

            for i in range(10):
                time.sleep(30)
                
                prediction_results = read_s3_file(
                    product_id=product_id,
                    s3_bucket=s3_bucket,
                    show_message=False 
                )

                if prediction_results is not None:
                    st.session_state.final_results = prediction_results
                    st.session_state.product_id = product_id
                    st.session_state.show_dashboard = True
                    st.rerun() 
                    break
            else:
                st.error("Não foi possível obter os resultados após 10 tentativas.")

main()