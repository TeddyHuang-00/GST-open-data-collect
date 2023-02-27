import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from scipy.optimize import curve_fit

st.set_page_config(
    page_title="GST酶活数据自动处理",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="collapsed",
)

weekdays = {
    1: "周一",
    2: "周二",
    3: "周三",
    4: "周四",
    5: "周五",
    6: "周六",
    7: "周日",
}

# Layout
st.title("📈GST酶活数据自动处理")
DATA, PROOF, RESULT = st.tabs(["提交数据", "数学推导", "拟合结果"])

if "template" not in st.session_state:
    st.session_state["template"] = pd.read_csv("./template.csv")


@st.cache_data
def save_data(name: str, ID: str, group: str, cls: str, data: pd.DataFrame) -> None:
    data.set_index(data.columns[0]).to_csv(f"./data/{cls}-{group}-{name}-{ID}.csv")


# @st.cache_data
def load_text(file_path: str):
    with open(file_path, "r") as f:
        return f.read()


def is_valid_input() -> bool:
    if len(st.session_state["NAME"]) == 0:
        st.warning("请输入姓名", icon="⚠️")
        return False
    elif len(st.session_state["ID"]) < 10:
        st.warning("请输入正确的学号", icon="⚠️")
        return False
    elif st.session_state["GROUP"] < 1 or st.session_state["GROUP"] > 6:
        st.warning("请输入正确的组号", icon="⚠️")
        return False
    elif (
        len(st.session_state["DATA"]) != 9 or len(st.session_state["DATA"].columns) != 8
    ):
        st.error("数据不完整，请检查是否正确填写！", icon="❌")
        return False
    st.success("提交成功！", icon="🎉")
    return True


# Modeling enzyme kinetics
def model(t, K, S=None):
    if S is None:
        S = st.session_state["S"]
    epsilon = st.session_state["epsilon"]
    L = st.session_state["L"]
    return (1 - np.exp(-K * t)) * S * epsilon * L


def fit_data(Abs):
    t = st.session_state["T"]
    if st.session_state["fix_total"]:
        guess = [0.1]
        bounds = ([0], [10])
    else:
        guess = [0.1, st.session_state["S"]]
        bounds = ([0, 0], [10, st.session_state["S"]])
    popt, pcov = curve_fit(
        f=model,
        xdata=t,
        ydata=Abs,
        p0=guess,
        bounds=bounds,
    )
    return popt


def fit_and_plot():
    t = st.session_state["T"]
    Abs = st.session_state["Abs"]
    popt = fit_data(Abs)
    K_estimate = popt[0]
    if st.session_state["fix_total"]:
        S_estimate = st.session_state["S"]
    else:
        S_estimate = popt[1]
    tt = np.linspace(t[0], t[-1], 100)
    fit = model(tt, *popt)
    upper = model(tt, *popt * 1.025)
    lower = model(tt, *popt * 0.975)
    R_squared = np.corrcoef(Abs, model(t, *popt))[0, 1] ** 2
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.plot(t, Abs, "o", color="tab:blue", label="Raw data")
    ax.plot(tt, fit, "-", color="tab:orange", label="Fitted curve")
    ax.fill_between(tt, lower, upper, color="tab:orange", alpha=0.2)
    ax.set_xlabel("Time(min)")
    ax.set_ylabel("$Abs_{340}$(a.u.)")
    ax.set_title(f"Fit of Abs data, R$^2$={R_squared:f}")
    ax.legend()
    st.pyplot(fig)
    st.markdown(
        load_text("./assets/param.md")
        .replace("PLACE_HOLDER_ESTIMATED_K", f"{K_estimate:.3f}")
        .replace("PLACE_HOLDER_ESTIMATED_S", f"{S_estimate:.3f}")
    )
    return K_estimate, S_estimate


with PROOF:
    st.markdown(load_text("./assets/proof.md"))

with DATA:
    with st.form("基本信息"):
        colName, colId, colClass, colGroup = st.columns(4)
        with colName:
            st.text_input(
                label="姓名",
                key="NAME",
            )
        with colId:
            st.text_input(
                label="学号",
                value="2000000000",
                max_chars=10,
                key="ID",
            )
        with colClass:
            st.selectbox(
                label="班级",
                options=list(weekdays.values()),
                key="CLASS",
            )
        with colGroup:
            st.selectbox(
                label="组号",
                options=[1, 2, 3, 4, 5, 6],
                key="GROUP",
            )
        st.caption(
            "表中各列分别代表 :red['时间 | 电动匀浆器 | 玻璃匀浆器 | 珠磨均质器 | pH6.0 | pH6.5 | pH7.0 | pH7.5']，数据如有复用也请完整填写，0min处数值应为0或近似于0"
        )
        st.session_state["DATA"] = st.experimental_data_editor(
            st.session_state["template"],
            key="DATA_EDITOR",
            use_container_width=True,
            num_rows="fixed",
        ).dropna()
        submit = st.form_submit_button(
            label="提交数据",
            help="新提交数据会自动覆盖此前记录",
        )
        if submit:
            st.session_state["IS_DATA_VALID"] = is_valid_input()
            if st.session_state["IS_DATA_VALID"]:
                save_data(
                    st.session_state["NAME"],
                    st.session_state["ID"],
                    st.session_state["GROUP"],
                    st.session_state["CLASS"],
                    st.session_state["DATA"],
                )


with RESULT:
    if not st.session_state.get("IS_DATA_VALID", False):
        st.warning("请先提交数据，再查看拟合结果", icon="⚠️")
        st.stop()
    with st.expander("数据选择", expanded=False):
        data = st.session_state["DATA"]
        st.selectbox(label="选择处理数据", options=data.columns[1:], key="Choice")
        st.session_state["T"] = data.iloc[:, 0].values
        st.session_state["Abs"] = data[st.session_state["Choice"]].values
        st.write("体系参数")
        colsA = [st.columns(3) for _ in range(2)]
        with colsA[0][0]:
            st.number_input(
                label="GSH终浓度(mM)",
                min_value=0.0,
                max_value=10.0,
                value=1.0,
                step=0.001,
                format="%.3f",
                key="S",
            )
        with colsA[0][1]:
            st.number_input(
                label="含酶样品加样量(μL)",
                min_value=0.0,
                max_value=10.0,
                value=3.0,
                step=0.001,
                format="%.3f",
                key="E",
            )
        with colsA[0][2]:
            st.number_input(
                label="体系总体积(mL)",
                min_value=0.0,
                max_value=5.0,
                value=3.0,
                step=0.001,
                format="%.3f",
                key="V",
            )
        with colsA[1][0]:
            st.checkbox(
                label="固定GSH浓度",
                value=False,
                help="固定后所输入的GSH终浓度将仅作参考，拟合结果中的浓度可能相差较大",
                key="fix_total",
            )
        with colsA[1][1]:
            st.number_input(
                label="消光系数(ε)",
                min_value=0.0,
                max_value=10.0,
                value=9.6,
                step=0.001,
                format="%.3f",
                key="epsilon",
            )
        with colsA[1][2]:
            st.number_input(
                label="比色杯光程(cm)",
                min_value=0.0,
                max_value=5.0,
                value=1.0,
                step=0.001,
                format="%.3f",
                key="L",
            )
        if st.button(label="按同样参数处理所有数据"):
            df = pd.DataFrame(
                {
                    "Method": [],
                    "Enzyme_Activity_tot": [],
                    "Enzyme_Activity_avg": [],
                    "S_0": [],
                    "R^2": [],
                }
            )
            for col_name in data.columns[1:]:
                popt = fit_data(data[col_name].values)
                K_estimate = popt[0]
                if st.session_state["fix_total"]:
                    S_estimate = st.session_state["S"]
                else:
                    S_estimate = popt[1]
                K_tot = (1 - np.exp(-K_estimate)) * S_estimate * st.session_state["V"]
                K_avg = (
                    (1 - np.exp(-K_estimate))
                    * S_estimate
                    * st.session_state["V"]
                    / st.session_state["E"]
                )
                fit = model(st.session_state["T"], *popt)
                R_squared = np.corrcoef(data[col_name].values, fit)[0, 1] ** 2
                df = pd.concat(
                    [
                        df,
                        pd.DataFrame(
                            {
                                "Method": [col_name],
                                "Enzyme_Activity_tot": [K_tot],
                                "Enzyme_Activity_avg": [K_avg],
                                "S_0": [S_estimate],
                                "R^2": [R_squared],
                            }
                        ),
                    ]
                )
            df = df.set_index("Method")
            st.dataframe(df)
            st.download_button(
                label="下载结果",
                data=df.to_csv(),
                file_name="result.csv",
                mime="text/csv",
            )

    with st.expander("计算结果", expanded=False):
        K_estimate, S_estimate = fit_and_plot()
        st.markdown(
            load_text("./assets/result.md")
            .replace(
                "PLACE_HOLDER_TOTAL_ENZYME_ACTIVITY",
                f"{(1 - np.exp(-K_estimate)) * S_estimate * st.session_state['V']:.4f}",
            )
            .replace(
                "PLACE_HOLDER_UNIT_ENZYME_ACTIVITY",
                f"{(1 - np.exp(-K_estimate))* S_estimate* st.session_state['V']/ st.session_state['E']:.4f}",
            )
        )
