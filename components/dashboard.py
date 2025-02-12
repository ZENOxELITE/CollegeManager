import streamlit as st
import plotly.express as px
from utils import get_all_students, get_all_teachers

def show_dashboard():
    st.header("Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Student Statistics")
        students_df = get_all_students()
        if not students_df.empty:
            # Department-wise distribution
            dept_counts = students_df['Department'].value_counts()
            fig1 = px.pie(
                values=dept_counts.values,
                names=dept_counts.index,
                title="Students by Department"
            )
            st.plotly_chart(fig1)

            # Year-wise distribution
            year_counts = students_df['Year'].value_counts()
            fig2 = px.bar(
                x=year_counts.index,
                y=year_counts.values,
                title="Students by Year"
            )
            st.plotly_chart(fig2)
        else:
            st.info("No student data available")

    with col2:
        st.subheader("Teacher Statistics")
        teachers_df = get_all_teachers()
        if not teachers_df.empty:
            # Department-wise distribution
            dept_counts = teachers_df['Department'].value_counts()
            fig3 = px.pie(
                values=dept_counts.values,
                names=dept_counts.index,
                title="Teachers by Department"
            )
            st.plotly_chart(fig3)

            # Total numbers
            st.metric("Total Students", len(students_df))
            st.metric("Total Teachers", len(teachers_df))
        else:
            st.info("No teacher data available")