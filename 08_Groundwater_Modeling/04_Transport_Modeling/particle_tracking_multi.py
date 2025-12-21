import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.patches import Polygon

# --- Authors, institutions, and year
year = 2025 
authors = {
    "Edith Grießer":[1],
    "Steffen Birk":[1],
    "Thomas Reimann": [2]
    
}
institutions = {
    1: "University of Graz",
    2: "TU Dresden"
}
index_symbols = ["¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"]
author_list = [f"{name}{''.join(index_symbols[i-1] for i in indices)}" for name, indices in authors.items()]
institution_list = [f"{index_symbols[i-1]} {inst}" for i, inst in institutions.items()]
institution_text = " | ".join(institution_list)

st.set_page_config(page_title = "iNUX - Particle Tracking", page_icon=".\FIGS\iNUX_wLogo.png")

st.title('Groundwater Particle Tracking')
st.header('Visualizing Groundwater Flow Paths and Travel Times for :rainbow[multiple particles]', divider = 'green')

st.markdown("""
  This app demonstrates how a conceptual particle is advected through a groundwater system by the subsurface flow field.
  
  Groundwater flow at the aquifer scale is governed by Darcy’s law, which relates fluid flux in porous media to hydraulic gradients and aquifer properties and forms the theoretical foundation of groundwater flow modeling (Darcy, 1856).
  
  By following the trajectory of a single particle over time, the app adopts a Lagrangian particle-tracking perspective, emphasizing advective transport along flow paths rather than concentration changes at fixed locations.
  
  This approach is widely used to analyze groundwater travel times and flow paths under steady-state conditions, for example in particle-tracking methods coupled to groundwater flow models (Pollock, 1988; Zheng & Bennett, 2002).""")

col1, col2, col3 = st.columns([1,1,1])
with col1:
    with st.expander('Particle and tracking characteristics'):
        x0 = st.slider('Position where the particle enters groundwater  \n$x_0$ (m)',1,400,200,1)
        t_set = st.slider('Time since particle reached the groundwater table  \n$t$ (years)',0,100,20,1)
        n_particles = st.select_slider("Number of particles", options=[1, 3, 5, 7, 9, 11, 13, 15], value=1)
        dx = st.slider("Horizontal spacing between neighboring particles  \n$\\Delta x$ (m)",1, 200, 20, 1)
with col2:
    q = st.slider('Infiltration rate (recharge)  \n$q$ (m/year)',0.01,0.4,0.2,0.01)

with col3:
    with st.expander('Aquifer characteristics'):
        D = st.slider('Average aquifer thickness  \n$b$ (m)',5,100,30,1)
        n0 = st.slider('Effective porosity  \n$n_0$ (%)',1,100,20,1)

def calc_x(x0,q,t,D,n0):
    x=x0*np.exp((q*t)/(D*(n0*0.01)))
    return x

def calc_d(x0,q,t,D,n0):
    d=D*(1-np.exp(-((q*t)/(D*(n0*0.01)))))
    return d

# define values
t = np.arange(1001)

x = calc_x(x0,q,t,D,n0)
d = calc_d(x0,q,t,D,n0)

# --- Particle bundle entry points (centered at x0)
k_max = (n_particles - 1) // 2                 # e.g., 5 -> 2 gives offsets [-2,-1,0,1,2]
offsets = np.arange(-k_max, k_max + 1)         # integer offsets
x0_all = x0 + offsets * dx                     # entry x for each particle

# Filter particles that would start left of x=0 (not shown)
mask_show = x0_all >= 0
x0_show = x0_all[mask_show]
n_hidden = int((~mask_show).sum())


# create a plot
fig,ax=plt.subplots(figsize=(8,10))

plt.title('Particle Tracking Visualization', fontsize=16)
plt.xlabel(r'x in m', fontsize=14)
plt.ylabel('aquifer thickness\nin m', fontsize=14)
    
ax.spines[['bottom','right']].set_visible(False)
ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
ax.set_ylim(-5,100)
ax.set_xlim(0, 1000)
ax.invert_yaxis()

# --- Center y-label at a specific data y-position
y_target = (D-5) / 2          # choose any data value (e.g. mid-aquifer)

ax.yaxis.set_label_coords(-0.06, y_target)
ax.get_yaxis().get_label().set_transform(ax.get_yaxis_transform())

# Define y-ticks starting at 0
yticks = np.arange(0, D + 1, 5)   # change step if needed
ax.set_yticks(yticks)

# Move x-axis to aquifer bottom
ax.spines['bottom'].set_position(('data', D))

# Clean spines
ax.spines['top'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)

# X-axis only at y = D
ax.tick_params(axis='x', bottom=True, labelbottom=True,
               top=False, labeltop=False)

# Aquifer base line
ax.axhline(D, color='black', linewidth=1.5)
ax.vlines(x=0, ymin=0, ymax=D, color='black', linewidth=1.5)

# Plot the values
# --- Plot all particle paths
for x0_i in x0_show:
    x_i = calc_x(x0_i, q, t, D, n0)
    ax.plot(x_i, d, linewidth=1, color = 'steelblue' )
    
# --- Highlight the central particle (if it is visible)
x_c = calc_x(x0, q, t, D, n0)
ax.plot(x_c, d, linewidth=2, color='darkblue')  # slightly thicker

plt.axhspan(0,D,facecolor='cornflowerblue', alpha=0.3)   # groundwater body
tgl = [[100,0],[90, -2],[110, -2]] # water triangle
ax.add_patch(Polygon(tgl))
ax.hlines(0, 90, 110) #(y,x1,x2)
ax.hlines(0.5, 95, 105)
ax.hlines(1, 98, 102)

# Marker for the central particle at selected time
ax.plot(x_c[t_set], d[t_set], color='deeppink', marker='o')

# --- Grey markers for all non-central particles at t_set
for x0_i in x0_show:
    if x0_i == x0:
        continue  # skip central particle
    x_i = calc_x(x0_i, q, t, D, n0)
    ax.plot(
        x_i[t_set],
        d[t_set],
        marker='o',
        color='pink',
        markersize=4,
        linestyle='None'
    )

# Reference lines at the central particle position
ax.hlines(d[t_set],xmin=0, xmax = x_c[t_set],  linestyle=':', colors='grey')
ax.vlines(x_c[t_set],ymin=d[t_set], ymax=D, linestyle=':', colors='grey')

red_dot = mlines.Line2D([],[],color='deeppink',marker='o',linestyle='', markersize=7,     # legent for the marker
                            label=f'central particle: t = {t_set} [years], z = {d[t_set]:.2f} [m], x = {x[t_set]:.2f} [m]')
ax.legend(handles=[red_dot], loc='upper right')

if n_hidden > 0:
    st.warning(
        f"{n_hidden} particle(s) not shown because their entry point would be at $x$ < 0 m. "
        f"(Central $x_0$ = {x0} m, $\Delta x$ = {dx} m, n = {n_particles})"
    )
    
st.pyplot(fig)

st.markdown('---')

columns_lic = st.columns((5,1))
with columns_lic[0]:
    st.markdown(f'Developed by {", ".join(author_list)} ({year}). <br> {institution_text}', unsafe_allow_html=True)
with columns_lic[1]:
    st.image('FIGS/CC_BY-SA_icon.png')
