import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Equal Dashboard", initial_sidebar_state="auto")

@st.cache_data
def load_data(file):
  return pd.read_excel(rf"excel_data/{file}")

df_fam_prod_venda = load_data("df_fam_prod_venda.xlsx")
df_fam_prod_venda_timed = load_data("df_fam_prod_venda_timed.xlsx")
df_saleBranch = load_data("df_saleBranch.xlsx")

df_fam_prod_venda_mut = df_fam_prod_venda

KEY_COUNTER = 0

def get_unique_key(prefix="widget"):
    global KEY_COUNTER
    KEY_COUNTER += 1
    return f"{prefix}_{KEY_COUNTER}"

with st.container():
    st.title("Dashboard gerencial")

with st.sidebar:
    selected = option_menu(
        menu_title = "Relatórios",
        options = ["Produtos", "Filiais" ,"Dados"],
        icons = ["box", "building" ,"book"],
        menu_icon = "house",
        default_index = 0
        )
if selected == "Produtos":
    st.subheader(":red[Relatórios]")
        
    with st.container():   
        st.write("Famílias: ")
        df_fam_prod_venda_mut["descricao_codigo"] = df_fam_prod_venda_mut.apply(lambda x: f"{x['codigo_familia']} - {x['descricaofamilia']}", axis=1)
        
        df_fam_prod_venda_group = df_fam_prod_venda_mut.groupby(['descricao_codigo', 'codigo_familia'])['lucro_produto'].sum().reset_index()
        
        number_filter_fam = int(st.slider("Famílias de produtos a visualizar: ", 1, 75, 7))
        st.write("---")
        df_fam_prod_venda_order = st.selectbox("Ordenação: ", ["Decrescente", "Crescente"], key=get_unique_key())
        
        df_fam_prod_venda_group = df_fam_prod_venda_group.sort_values(by='lucro_produto', ascending=(df_fam_prod_venda_order == "Crescente")).reset_index(drop=True)
            
        df_fam_prod_venda_filter_order = df_fam_prod_venda_group.head(number_filter_fam) 

        fig_order_by_fam_prod_venda = go.Figure(data=[go.Bar(x=df_fam_prod_venda_filter_order['descricao_codigo'], y=df_fam_prod_venda_filter_order['lucro_produto'])])
        fig_order_by_fam_prod_venda.update_layout(xaxis=dict(tickmode='linear'), yaxis=dict(title='LUCRO POR FAMÍLIA',  titlefont=dict(color='rgb(0,210,0)', size=15, family='Montserrat, sans-serif')))
        st.plotly_chart(fig_order_by_fam_prod_venda)
        
        def render_by_role(role):
            if role == "lucro_produto":
                default_value_slider_fam = 5
                default_value_slider_prod = 3
                text_famOrder1 = "Maior lucro por família"
                text_famOrder2 = "Menor lucro por família"
                text_prodOrder1 = "Maior lucro por produto"
                text_prodOrder2 = "Menor lucro por produto"
            if role == "quantidade":
                default_value_slider_fam = 2
                default_value_slider_prod = 4
                text_famOrder1 = "Famílias que mais vendem"
                text_famOrder2 = "Famílias que menos vendem"
                text_prodOrder1 = "Produtos que mais vendem"
                text_prodOrder2 = "Produtos que menos vendem"
    
            st.write("Produtos: ")
            df_fam_prod_venda_filter_order_search = df_fam_prod_venda_mut.groupby("codigo_familia")[role].sum().reset_index()
            
            fam_search_filter, prod_search_filter = st.columns(2)
            with fam_search_filter:
                number_filter_fam_search = int(st.slider("Famílias a visualizar: ", 0, 40, default_value_slider_fam))
                df_fam_prod_venda_order_fam_search = st.selectbox("Ordenação: ", [text_famOrder1, text_famOrder2])
            with prod_search_filter:
                number_filter_prod_search = int(st.slider("Produtos a visualizar: ", 0, 10, default_value_slider_prod))
                df_fam_prod_venda_order_prod_search = st.selectbox("Ordenação: ", [text_prodOrder1, text_prodOrder2])
            st.write("---")
            
            df_fam_prod_venda_filter_order_search = df_fam_prod_venda_filter_order_search.sort_values(by=role, ascending=(df_fam_prod_venda_order_fam_search == text_famOrder2)).reset_index(drop=True)
            df_fam_prod_venda_filter_order_search = df_fam_prod_venda_filter_order_search["codigo_familia"].head(number_filter_fam_search)
            
            df_fam_prod_search_prod_top = pd.merge(df_fam_prod_venda_filter_order_search, df_fam_prod_venda_mut[["codigo_familia", role, "descricaoproduto", "descricao_codigo"]], on="codigo_familia", how="inner").sort_values(by=role, ascending=False).reset_index(drop=True)
            df_fam_prod_search_prod_top = df_fam_prod_search_prod_top.groupby('codigo_familia').apply(lambda x: x.nlargest(number_filter_prod_search, role).reset_index(drop=True) if df_fam_prod_venda_order_prod_search == text_prodOrder1 else x.nsmallest(number_filter_prod_search, role)).reset_index(drop=True)

            prod_a, prod_b = st.columns(2)
            
            i = 0
            for cod in df_fam_prod_venda_filter_order_search.to_list():
                df_fam_prod_search_prod_top_filter = df_fam_prod_search_prod_top[df_fam_prod_search_prod_top["codigo_familia"] == cod]
                if i % 2 == 0:
                    with prod_a:
                        st.write(f"Família - Descrição: :green[{df_fam_prod_search_prod_top_filter["descricao_codigo"].iloc[0]}]")
                        st.bar_chart(df_fam_prod_search_prod_top_filter, x="descricaoproduto", y=role)
                    i+=1
                else:
                    with prod_b:
                        st.write(f"Família - Descrição: :green[{df_fam_prod_search_prod_top_filter["descricao_codigo"].iloc[0]}]")
                        st.bar_chart(df_fam_prod_search_prod_top_filter, x="descricaoproduto", y=role)
                    i+=1
        
        with st.expander("PRODUTOS POR FAMÍLIA"):
            render_by_role("lucro_produto")
                    
        with st.expander("PRODUTOS POR QUANTIDADE"):
            render_by_role("quantidade")
            
        with st.expander("FATURAMENTO POR FAMÍLIA"):
            df_fam_prod_venda_timed["data"] = pd.to_datetime(df_fam_prod_venda_timed['ano'].astype(str) + '-' + df_fam_prod_venda_timed['mes'].astype(str))
            
            calcular_dif_fat = lambda row: row["valor_monetario_total"] - df_fam_prod_venda_timed.loc[df_fam_prod_venda_timed["data"].idxmin(), "valor_monetario_total"]
            df_fam_prod_venda_timed["dif_fat"] = df_fam_prod_venda_timed.apply(calcular_dif_fat, axis=1)
            
            number_filter_fam_timed = int(st.slider("Famílias de produtos a visualizar: ", 1, 75, 5))
            df_fam_prod_venda_order_timed = st.selectbox("Ordenação: ", ["Maiores faturamentos", "Menores faturamentos"], key=get_unique_key())
            df_fam_most_sales = df_fam_prod_venda_group.sort_values(by='lucro_produto', ascending=(df_fam_prod_venda_order_timed == "Menores faturamentos")).reset_index(drop=True)
            
            df_fam_most_sales_timed = pd.merge(df_fam_most_sales.head(number_filter_fam_timed), df_fam_prod_venda_timed[["codigo_familia", "mes", "ano", "valor_monetario_total", "data", "dif_fat"]], on="codigo_familia", how="inner")
            
            for cod_fam in df_fam_most_sales["codigo_familia"].head(number_filter_fam_timed).to_list():
                df_fam_most_sales_timed_filter = df_fam_most_sales_timed[df_fam_most_sales_timed["codigo_familia"] == cod_fam]
                df_fam_most_sales_timed_filter_order = df_fam_most_sales_timed_filter.sort_values(by="data", ascending=True).reset_index(drop=True)
                st.write(f"Família - Descrição: :green[{df_fam_most_sales_timed_filter_order["descricao_codigo"].iloc[0]}]")
                st.line_chart(df_fam_most_sales_timed_filter_order, x="data", y="valor_monetario_total")

if selected == "Filiais":
    with st.container():
        st.write("")
        st.markdown("#### :red[Faturamento geral das filiais nos últimos 3 anos:]")
        df_saleBranch_mut = df_saleBranch
        df_saleBranch_groupBranch = df_saleBranch_mut.groupby(["filial_venda"])["valor_monetario_total"].sum().reset_index()
        
        df_saleBranch_groupBranch_date = df_saleBranch_mut.groupby(["filial_venda", "mes", "ano"])["valor_monetario_total"].sum().reset_index()
        df_saleBranch_groupBranch_date["data_venda"] = pd.to_datetime(df_saleBranch_groupBranch_date['ano'].astype(str) + '-' + df_saleBranch_groupBranch_date['mes'].astype(str))
        
        st.bar_chart(df_saleBranch_groupBranch, x="filial_venda", y="valor_monetario_total")
        
        with st.expander("CRESCIMENTO DE FATURAMENTO"):
            st.write("Famílias que mais cresceram/decresceram")
            number_filter_fam_timed_fat = int(st.slider("Famílias de produtos a visualizar: ", 1, 75, 4))
            df_fam_prod_venda_order_timed_fat = st.selectbox("Ordenação: ", ["Famílias que mais cresceram", "Famílias que menos cresceram"], key=get_unique_key())
            
            df_fam_prod_venda_timed["data"] = pd.to_datetime(df_fam_prod_venda_timed['ano'].astype(str) + '-' + df_fam_prod_venda_timed['mes'].astype(str))
            calcular_dif_fat = lambda row: row["valor_monetario_total"] - df_fam_prod_venda_timed.loc[df_fam_prod_venda_timed["data"].idxmin(), "valor_monetario_total"]
            df_fam_prod_venda_timed["dif_fat"] = df_fam_prod_venda_timed.apply(calcular_dif_fat, axis=1)
            
            df_fam_prod_venda_timed_fat = df_fam_prod_venda_timed.groupby(["codigo_familia", "descricaofamilia"])["dif_fat"].sum().reset_index()
            df_fam_prod_venda_timed_fat = df_fam_prod_venda_timed_fat.sort_values(by="dif_fat", ascending=(df_fam_prod_venda_order_timed_fat == "Famílias que menos cresceram")).reset_index(drop=True)
            
            df_most_variable_fat = df_fam_prod_venda_timed_fat.head(number_filter_fam_timed_fat)
            df_most_variable_fat["descricao_codigo"] = df_most_variable_fat.apply(lambda x: f"{x['codigo_familia']} - {x['descricaofamilia']}", axis=1)
            
            st.write(f"Família - Descrição: :green[{df_most_variable_fat["descricao_codigo"].iloc[0]}]")
            st.bar_chart(df_most_variable_fat, x="descricao_codigo", y="dif_fat")
                    
        with st.expander("FATURAMENTO DETALHADO"):
            chosen_branch = st.multiselect("Filiais a visualisar: ", df_saleBranch_groupBranch["filial_venda"].to_list())
            
            for filial in chosen_branch:
                df_filial_chosen = df_saleBranch_groupBranch_date[df_saleBranch_groupBranch_date["filial_venda"] == filial]
                df_filial_chosen_order = df_filial_chosen.sort_values(by="data_venda", ascending=True).reset_index(drop=True)
                st.write(f"Filial N°: :green[{filial}]")
                st.line_chart(df_filial_chosen_order, x="data_venda", y="valor_monetario_total")
                
        with st.expander("FATURAMENTO POR VENDEDOR"):
            number_filter_branchEmpl = int(st.slider("Vendedores a visualizar: ", 1, 50, 10))
            df_fam_prod_venda_order_empl = st.selectbox("Ordenação: ", ["Vendedores que mais venderam", "Vendedores que menos venderam"])
            st.write("---")
            
            df_saleBranch_groupEmpl = df_saleBranch.groupby(["codigo_vendedor", "nome_vendedor"])["valor_monetario_total"].sum().reset_index()
            df_saleBranch_groupEmpl["codigo_nome"] = df_saleBranch_groupEmpl.apply(lambda x: f"{x['codigo_vendedor']} - {x['nome_vendedor']}", axis=1)
            df_saleBranch_groupEmpl = df_saleBranch_groupEmpl.sort_values(by="valor_monetario_total", ascending=(df_fam_prod_venda_order_empl == "Vendedores que menos venderam")).reset_index(drop=True)
            df_saleBranch_groupEmpl = df_saleBranch_groupEmpl.head(number_filter_branchEmpl)
            st.bar_chart(df_saleBranch_groupEmpl, x="codigo_nome", y="valor_monetario_total")

if selected == "Dados":
    st.subheader("Dados utilizados: ")
    st.markdown("#### :orange[Família, produtos e quantidade]")
    st.write(df_fam_prod_venda_mut)
    st.write("---")
    st.markdown("#### :orange[Vendas de produtos pelo tempo]")
    st.write(df_fam_prod_venda_timed)
    st.write("---")
    st.markdown("#### :orange[Vendedores e Filiais]")
    st.write(df_saleBranch)