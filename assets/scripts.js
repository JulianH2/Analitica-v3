window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        // Ahora aceptamos ids como segundo argumento (aunque no lo usemos, Dash lo envía)
        switch_graph_theme: function(theme, ids, figures) {
            
            // Si no hay tema, asumir dark por defecto para evitar parpadeos
            const currentTheme = theme || 'dark';
            document.documentElement.setAttribute('data-mantine-color-scheme', currentTheme);

            if (!figures || !Array.isArray(figures)) {
                return window.dash_clientside.no_update;
            }

            const templateName = currentTheme === 'dark' ? 'zam_dark' : 'zam_light';

            return figures.map(fig => {
                if (!fig) return null;

                // Clonamos la figura para no mutar el estado directamente
                const newFig = JSON.parse(JSON.stringify(fig));

                if (!newFig.layout) newFig.layout = {};

                // 1. Forzamos el template correcto
                newFig.layout.template = templateName;
                
                // 2. Limpiamos colores de fondo para transparencia
                newFig.layout.paper_bgcolor = "rgba(0,0,0,0)";
                newFig.layout.plot_bgcolor = "rgba(0,0,0,0)";
                
                // 3. Forzamos el color de fuente global si es necesario
                // Esto ayuda si alguna gráfica rebelde no quiere cambiar
                const fontColor = currentTheme === 'dark' ? '#ffffff' : '#1e293b';
                if (!newFig.layout.font) newFig.layout.font = {};
                newFig.layout.font.color = fontColor;

                return newFig;
            });
        }
    }
});

// Mantener la carga inicial del tema
(function() {
    try {
        const dashStore = localStorage.getItem('theme-store');
        if (dashStore) {
            const theme = JSON.parse(dashStore).data;
            document.documentElement.setAttribute('data-mantine-color-scheme', theme || 'dark');
        }
    } catch (e) {}
})();