window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        switch_graph_theme: function(theme, ids, figures) {
            
            const currentTheme = theme || 'dark';
            document.documentElement.setAttribute('data-mantine-color-scheme', currentTheme);

            if (!figures || !Array.isArray(figures)) {
                return window.dash_clientside.no_update;
            }

            const templateName = currentTheme === 'dark' ? 'zam_dark' : 'zam_light';

            return figures.map(fig => {
                if (!fig) return null;

                const newFig = JSON.parse(JSON.stringify(fig));

                if (!newFig.layout) newFig.layout = {};

                newFig.layout.template = templateName;
                
                newFig.layout.paper_bgcolor = "rgba(0,0,0,0)";
                newFig.layout.plot_bgcolor = "rgba(0,0,0,0)";
                
                const fontColor = currentTheme === 'dark' ? '#ffffff' : '#1e293b';
                if (!newFig.layout.font) newFig.layout.font = {};
                newFig.layout.font.color = fontColor;

                return newFig;
            });
        }
    }
});

(function() {
    try {
        const dashStore = localStorage.getItem('theme-store');
        if (dashStore) {
            const theme = JSON.parse(dashStore).data;
            document.documentElement.setAttribute('data-mantine-color-scheme', theme || 'dark');
        }
    } catch (e) {}
})();