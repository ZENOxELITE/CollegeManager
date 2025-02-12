import streamlit as st
import plotly.express as px

def show_dashboard():
    st.header("Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Student Statistics")
        if not st.session_state.students.empty:
            # Department-wise distribution
            dept_counts = st.session_state.students['Department'].value_counts()
            fig1 = px.pie(
                values=dept_counts.values,
                names=dept_counts.index,
                title="Students by Department"
            )
            st.plotly_chart(fig1)

            # Year-wise distribution
            year_counts = st.session_state.students['Year'].value_counts()
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
        if not st.session_state.teachers.empty:
            # Department-wise distribution
            dept_counts = st.session_state.teachers['Department'].value_counts()
            fig3 = px.pie(
                values=dept_counts.values,
                names=dept_counts.index,
                title="Teachers by Department"
            )
            st.plotly_chart(fig3)

            # Total numbers
            st.metric("Total Students", len(st.session_state.students))
            st.metric("Total Teachers", len(st.session_state.teachers))
        else:
            st.info("No teacher data available")