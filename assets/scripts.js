window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        switch_graph_theme: function(theme, figures) {
            if (!theme) return figures;

            // 1. Aplicar el tema al HTML para que Mantine lo reconozca
            document.documentElement.setAttribute('data-mantine-color-scheme', theme);
            
            if (!figures || !Array.isArray(figures)) return figures;

            // 2. Sincronizar Plotly
            const template = theme === 'dark' ? 'zam_dark' : 'zam_light';
            
            return figures.map(fig => {
                if (!fig || !fig.layout) return fig;
                const newFig = JSON.parse(JSON.stringify(fig));
                newFig.layout.template = template;
                newFig.layout.paper_bgcolor = "rgba(0,0,0,0)";
                newFig.layout.plot_bgcolor = "rgba(0,0,0,0)";
                return newFig;
            });
        }
    }
});

/** * Lógica de persistencia pura: 
 * Lee el dcc.Store de Dash (que vive en localStorage) 
 * y aplica el tema al HTML antes de que se vea la página.
 */
(function() {
    try {
        const dashStore = localStorage.getItem('theme-store');
        if (dashStore) {
            const theme = JSON.parse(dashStore).data;
            document.documentElement.setAttribute('data-mantine-color-scheme', theme || 'dark');
        }
    } catch (e) {
        console.error("Error cargando el tema persistente", e);
    }
})();