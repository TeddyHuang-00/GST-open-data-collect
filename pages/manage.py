import os
import smtplib
from collections import defaultdict
from email.mime.text import MIMEText
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from scipy.optimize import curve_fit

st.title("后台管理")

if "login" not in st.session_state:

    def get_pin(addr):
        dt = datetime.now()
        pin = str(hash(dt.strftime("%Y-%m") + addr))
        for s in st.secrets["admin"]["salt"]:
            pin = str(hash(pin + s))
        return pin[-6:]

    def send_email(subject, body, sender, recipients, password):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = f"DO NOT REPLY <{sender}>"
        msg["To"] = recipients
        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
        smtp_server.quit()
        st.success("邮件已重新发送")

    st.subheader("管理员登陆")
    with st.form("管理员登陆"):
        addr = st.text_input("邮箱地址")
        pin = st.text_input(
            "验证码", type="password", help="如果您第一次登陆，请先点击“登陆”按钮获取验证码，验证码当月有效"
        )
        if st.form_submit_button("登陆"):
            if addr in st.secrets["admin"]["address"]:
                if pin == get_pin(addr):
                    st.session_state["login"] = True
                    st.experimental_rerun()
                else:
                    st.error("验证码错误，邮件正在重新发送，请耐心等候")
                    send_email(
                        "Your temporary pin code",
                        "Your temporary pin code is:\n\n" + get_pin(addr),
                        st.secrets["email"]["account"],
                        addr,
                        st.secrets["email"]["passwd"],
                    )
            else:
                st.error("您不是管理员")
    st.stop()


file_list = [
    file_name for file_name in os.listdir("data") if file_name.endswith(".csv")
]
info_list = sorted(
    [tuple(file_name.strip(".csv").split("-")) for file_name in file_list],
    key=lambda x: (x[0], x[1], x[3]),
)

SUBMIT, MANAGE, SUMMARY = st.tabs(["提交情况", "数据管理", "数据汇总"])

with SUBMIT:
    counter = defaultdict(lambda: defaultdict(int))
    for info in info_list:
        counter[info[0]][f"{info[1]} 组"] += 1
    st.bar_chart(pd.DataFrame(counter).T, use_container_width=True)

with MANAGE:
    all_days = sorted(set([info[0] for info in info_list]))
    day_selected = st.multiselect("选择班级", all_days, all_days)
    day_filtered = [info for info in info_list if info[0] in day_selected]

    all_groups = sorted(set([info[1] for info in info_list]))
    group_selected = st.multiselect("选择小组", all_groups, all_groups)
    group_filtered = [info for info in day_filtered if info[1] in group_selected]

    df_list = [
        pd.read_csv("data/" + "-".join(info) + ".csv") for info in group_filtered
    ]

    checkbox, _, display, _, delete = st.columns([2, 6, 3, 6, 3])
    with checkbox:
        st.subheader("导出结果")
    with display:
        st.subheader("数据管理")
    with delete:
        st.subheader("永久删除")
    for idx, (info, df) in enumerate(zip(group_filtered, df_list)):
        checkbox, display, delete = st.columns([1, 7, 2])
        with checkbox:
            st.checkbox(
                "导出结果", value=True, key=info_list[idx][-1], label_visibility="hidden"
            )
        with display:
            with st.expander(" - ".join(info)):
                df_list[idx] = st.experimental_data_editor(
                    df,
                    key=" - ".join(info),
                    use_container_width=True,
                    num_rows="dynamic",
                )
        with delete:
            with st.expander("删除"):
                st.caption("删除后无法恢复，请确认无误")
                if st.button("确认删除", key=" ".join(info), type="primary"):
                    os.remove("data/" + "-".join(info) + ".csv")
                    st.experimental_rerun()

with SUMMARY:
    weekday_zh2en = {
        "周一": "Mon",
        "周二": "Tue",
        "周三": "Wed",
        "周四": "Thu",
        "周五": "Fri",
        "周六": "Sat",
        "周日": "Sun",
    }
    weekday_en2zh = {
        "Mon": "周一",
        "Tue": "周二",
        "Wed": "周三",
        "Thu": "周四",
        "Fri": "周五",
        "Sat": "周六",
        "Sun": "周日",
    }

    cols = st.columns(4)
    with cols[0]:
        Total_Volume = st.number_input("体系总容量", 0.0, 10.0, 3.0, help="单位：mL")
    with cols[1]:
        GSH_concentration = st.number_input("GSH 浓度", 0.0, 10.0, 1.0, help="单位：mM")
    with cols[2]:
        Cache_Length = st.number_input(
            "比色皿光程", 0.0, 10.0, 1.0, help="单位：cm", disabled=True
        )
    with cols[3]:
        epsilon = st.number_input("GS-DNB 摩尔消光系数", 9.0, 10.0, 9.6, disabled=True)

    def model(t, K, S):
        return (1 - np.exp(-K * t)) * S * epsilon * Cache_Length

    def fit_data(t, Abs):
        guess = [0.1, GSH_concentration]
        bounds = ([0, 0], [10, GSH_concentration])
        popt, _ = curve_fit(
            f=model,
            xdata=t,
            ydata=Abs,
            p0=guess,
            bounds=bounds,
        )
        return popt

    if st.button(("重新" if "output" in st.session_state else "") + "处理所选数据"):
        wrong_format_list = [
            (info, df) for info, df in zip(info_list, df_list) if len(df) < 9
        ]
        correct_format_list = [
            (info, df) for info, df in zip(info_list, df_list) if len(df) >= 9
        ]
        if len(wrong_format_list) > 0:
            st.subheader("格式检查")
            st.warning("以下数据格式不正确，请检查")
            for info, df in wrong_format_list:
                with st.expander(" - ".join(info)):
                    st.write(df)

        collect = pd.DataFrame(
            {
                "Method": [],
                "Enzyme_Activity_tot": [],
                "Enzyme_Activity_avg": [],
                "S_estimate": [],
                "R_squared": [],
                "Method_Group": [],
                "Day": [],
                "Group": [],
                "Name": [],
                "Id": [],
            }
        )
        for (Day, Group, Name, Id), data in correct_format_list:
            t = data["Minute"].values
            for col_name in data.columns[1:]:
                Abs = data[col_name].values
                Abs[0] = 0
                popt = fit_data(t, Abs)
                fit = model(t, *popt)
                K_est, S_est = popt
                K_tot = (1 - np.exp(-K_est)) * S_est * Total_Volume
                R_squared = np.corrcoef(Abs, fit)[0, 1] ** 2
                collect = pd.concat(
                    [
                        collect,
                        pd.DataFrame(
                            {
                                "Method": col_name,
                                "Enzyme_Activity_tot": K_tot,
                                "Enzyme_Activity_avg": K_est,
                                "S_estimate": S_est,
                                "R_squared": R_squared,
                                "Method_Group": int(col_name[:2] == "pH"),
                                "Day": weekday_zh2en[Day],
                                "Group": Group,
                                "Name": hex(hash(Name) + hash(Id))[-8:],
                                "Id": Id,
                            },
                            index=[0],
                        ),
                    ],
                    ignore_index=True,
                )
        dedup = collect.drop_duplicates(
            subset=["Enzyme_Activity_tot", "Day", "Group", "Method"]
        )
        group_means = dedup.groupby(["Day", "Group"]).mean()["Enzyme_Activity_avg"]
        mean_means = group_means.mean()
        norm_params = group_means / mean_means
        # normalize data based on group
        df_new_column = dedup[["Enzyme_Activity_avg", "Day", "Group"]].copy()
        for idx, params in norm_params.items():
            day, group = idx
            df_new_column.loc[
                (df_new_column["Group"] == group) & (df_new_column["Day"] == day),
                "Enzyme_Activity_avg",
            ] /= params
        # add a column of noramlized data to dedup
        normalized = dedup.copy()
        normalized.insert(
            loc=list(dedup.columns).index("Enzyme_Activity_avg") + 1,
            column="Enzyme_Activity_avg_norm",
            value=df_new_column["Enzyme_Activity_avg"],
        )
        st.session_state["output"] = normalized

        st.info(
            f"数据处理完成，共处理{len(correct_format_list)}组数据，共计{len(dedup)}/{len(collect)}条有效数据"
        )

    if "output" in st.session_state:
        with st.expander("预览数据"):
            st.dataframe(st.session_state["output"], use_container_width=True)
        st.download_button(
            "下载全部结果",
            data=st.session_state["output"].to_csv(index=False),
            file_name="Total.csv",
            mime="text/csv",
        )
        for day in st.session_state["output"]["Day"].unique():
            st.download_button(
                f"下载{weekday_en2zh[day]}结果",
                data=st.session_state["output"][
                    st.session_state["output"]["Day"] == day
                ].to_csv(index=False),
                file_name=f"{day}.csv",
                mime="text/csv",
            )
