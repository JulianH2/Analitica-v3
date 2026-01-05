// assets/scripts.js

if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.clientside = {
    
    switch_graph_theme: function(theme_mode, current_figures) {
        // Mapeo de nombres de template
        const template_name = theme_mode === 'dark' ? 'zam_dark' : 'zam_light';
        
        // Validación defensiva: Si no hay figuras o no es un array, no hacer nada
        if (!current_figures || !Array.isArray(current_figures)) {
            return window.dash_clientside.no_update;
        }

        // Iterar y clonar
        const new_figures = current_figures.map(fig => {
            if (!fig) return null;
            
            // Clonación profunda segura para Plotly
            const new_fig = JSON.parse(JSON.stringify(fig));
            
            if (!new_fig.layout) new_fig.layout = {};
            
            // Inyectar el template correspondiente
            new_fig.layout.template = template_name;
            
            // Forzar repintado de fondo transparente por seguridad
            new_fig.layout.paper_bgcolor = "rgba(0,0,0,0)";
            new_fig.layout.plot_bgcolor = "rgba(0,0,0,0)";
            
            return new_fig;
        });

        return new_figures;
    }
};