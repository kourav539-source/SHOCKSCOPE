"""Shared case selections; financial assumptions remain independent of the case."""
import streamlit as st

OPTIONS = {
    'event': ['Strait of Hormuz disruption', 'Red Sea shipping crisis', 'Russia–Ukraine war'],
    'country': ['India', 'China', 'USA', 'Japan', 'Germany', 'Australia'],
    'industry': ['Energy', 'Aviation', 'Manufacturing', 'Agriculture', 'Logistics', 'Chemicals'],
}
DEFAULTS = {'event': OPTIONS['event'][0], 'country': 'India', 'industry': 'Aviation'}


def _key(field):
    return 'scope_case_' + field


def get_case(field):
    value = st.session_state.get(_key(field), DEFAULTS[field])
    return value if value in OPTIONS[field] else DEFAULTS[field]


def shared_select(label, field, key):
    """Mirror widget state before creation; callbacks update the persistent case."""
    current = get_case(field)
    st.session_state[_key(field)] = current
    if st.session_state.get(key) != current:
        st.session_state[key] = current

    def changed():
        value = st.session_state[key]
        if value in OPTIONS[field]:
            st.session_state[_key(field)] = value

    return st.selectbox(label, OPTIONS[field], index=None, key=key, on_change=changed)


def reset_case():
    for field, value in DEFAULTS.items():
        st.session_state[_key(field)] = value
