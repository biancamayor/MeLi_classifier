import streamlit as st
from src.scraper import scrape_reviews
from src.infer_comment_class import infer_comment_class

def main(product_id):
    csv_path = scrape_reviews(product_id=product_id)
    results = infer_comment_class(csv_path)
    return results

st.set_page_config(page_title="MeLi classifier", layout="wide")

st.markdown("""
<style>
/* fundo suave da página */
body, .stApp { background-color: #f6f7fb; }

/* centraliza a área de conteúdo e dá mais respiro */
.block-container { padding-top: 32px; }

/* estiliza QUALQUER formulário como um "card" branco */
div[data-testid="stForm"]{
  background: #ffffff;
  border-radius: 16px;
  padding: 28px 32px;
  box-shadow: 0 10px 24px rgba(0,0,0,.06);
  border: 1px solid rgba(0,0,0,.05);
}

/* input estilizado */
div[data-testid="stTextInput"] input {
  width: 100%;
  height: 40px;
  border-radius: 10px;
  border: 1px solid #F8F7FB;
  padding: 0 10px;
  background-color: #F2F2F2;
  color: #6b7280;
}

/* placeholder visível */
div[data-testid="stTextInput"] input::placeholder {
  color: #D0D3DC;
  opacity: 1;
}

/* botão estilizado */
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


if submit and product_id:
    placeholder = st.empty()  
    
    with placeholder.container(): 
        st.markdown(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 70vh;">
                <h4 style="color: black;">🔎 Buscando avaliações e gerando análise...</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    prediction = main(product_id)
    print(prediction)

    prediction_percent = prediction['positives_percent']
    product_name = prediction['product_name']
    negative_comments=prediction['negatives']
    analysis_confidence=prediction['confidence']
    total_comments=prediction['total_comments']

    prediction = prediction_percent

    bar_color = "#16a34a" if prediction >= 50 else "#dc2626"  
    
    placeholder.empty() 
    with placeholder.container():
        st.markdown(
            f"""
            <div style="text-align:center; margin-top:30px;">
                <h3 style="color:#111827; margin-bottom:5px;">{product_name}</h3>
                <p style="color:#6b7280; margin-top:0;">ID: {product_id}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
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
                <h2 style="color:{bar_color};">{prediction:.0f}%</h2>
                <p style="color:#111827;">Feedbacks {'Positivos' if prediction >= 50 else 'Negativos'}</p>
            </div>
        </div>
        <div style="margin-top:30px; display:flex; justify-content:center;">
            <div style="width:80%; background:#e5e7eb; height:14px; border-radius:10px;">
                <div style="width:{prediction}%; background:{bar_color}; height:100%; border-radius:10px;"></div>
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