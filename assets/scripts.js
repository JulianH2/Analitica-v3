(function () {
    try {
        console.log("🚀 Iniciando hidratación de tema...");
        
        const keys = Object.keys(localStorage);
        
        const themeKey = keys.find(k => k.includes('theme-store'));
        
        if (!themeKey) {
            console.log("ℹ️ No se encontró theme-store en localStorage.");
            return;
        }

        const raw = localStorage.getItem(themeKey);
        if (!raw) return;

        const parsed = JSON.parse(raw);

        const theme = (parsed && typeof parsed === 'object' && parsed.data) 
                      ? parsed.data 
                      : parsed;

        console.log(`✅ Tema detectado en storage: ${theme}`);

        if (theme === 'dark' || theme === 'light') {
            document.documentElement.setAttribute('data-mantine-color-scheme', theme);
        }
    } catch (e) {
        console.warn("⚠️ Falló la hidratación del tema:", e);
    }
})();

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        switch_graph_theme: function(theme, ids, figures) {
            const currentTheme = theme || 'dark';
            
            document.documentElement.setAttribute('data-mantine-color-scheme', currentTheme);

            if (!figures || !Array.isArray(figures)) {
                return window.dash_clientside.no_update;
            }

            const templateName = currentTheme === 'dark' ? 'zam_dark' : 'zam_light';
            const fontColor = currentTheme === 'dark' ? '#ffffff' : '#1e293b';

            return figures.map(fig => {
                if (!fig) return null;
                const newFig = JSON.parse(JSON.stringify(fig));
                
                if (!newFig.layout) newFig.layout = {};
                newFig.layout.template = templateName;
                newFig.layout.paper_bgcolor = "rgba(0,0,0,0)";
                newFig.layout.plot_bgcolor = "rgba(0,0,0,0)";
                
                if (!newFig.layout.font) newFig.layout.font = {};
                newFig.layout.font.color = fontColor;

                return newFig;
            });
        }
    }
});