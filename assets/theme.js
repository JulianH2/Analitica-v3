/* switch_graph_theme - Versión Final Unificada */
window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    switch_graph_theme: function (theme, ids, figures) {
      const currentTheme = theme || "dark";
      if (!figures || !Array.isArray(figures)) {
        return window.dash_clientside.no_update;
      }

      const isDark = currentTheme === "dark";
      const templateName = isDark ? "zam_dark" : "zam_light";

      // Colores semánticos según design_system.py
      const textColor = isDark ? "#e8eaed" : "#1d1d1b";
      const secondaryColor = isDark ? "#9ca3af" : "#808080";
      const tooltipBg = isDark ? "#3b4249" : "#ffffff";
      const gridColor = isDark ? "#4a5a68" : "#f2f2f2";

      return figures.map((fig) => {
        if (!fig) return null;
        const newFig = JSON.parse(JSON.stringify(fig));

        if (!newFig.layout) newFig.layout = {};

        // 1. Configuración Global de Layout
        newFig.layout.template = templateName;
        newFig.layout.paper_bgcolor = "rgba(0,0,0,0)";
        newFig.layout.plot_bgcolor = "rgba(0,0,0,0)";
        newFig.layout.font = {
          ...(newFig.layout.font || {}),
          color: textColor,
          family: "'Nexa', sans-serif"
        };

        // 2. Fix de Tooltips Global (Para Donas, Barras y Líneas)
        newFig.layout.hoverlabel = {
          bgcolor: tooltipBg,
          bordercolor: gridColor,
          font: { color: textColor, size: 12 }
        };

        // 3. Fix de Anotaciones (Texto central de Donas y Metas)
        if (newFig.layout.annotations) {
          newFig.layout.annotations.forEach((ann) => {
            ann.font = { ...(ann.font || {}), color: textColor };
          });
        }

        // 4. Ajustes por tipo de trazo (Traces)
        if (newFig.data) {
          newFig.data.forEach((trace) => {
            // GAUGES / INDICATORS
            if (trace.type === "indicator") {
              trace.number = {
                ...(trace.number || {}),
                font: { ...(trace.number?.font || {}), color: textColor }
              };

              if (trace.title) {
                trace.title.font = {
                  ...(trace.title.font || {}),
                  color: textColor
                };
              }

              if (trace.gauge) {
                trace.gauge.bgcolor = isDark
                  ? "rgba(255,255,255,0.05)"
                  : "rgba(0,0,0,0.05)";

                if (trace.gauge.axis) {
                  trace.gauge.axis.tickfont = {
                    ...(trace.gauge.axis.tickfont || {}),
                    color: secondaryColor
                  };
                }
              }
            }


            // DONUTS / PIE (Bordes de rebanadas)
            if (trace.type === "pie") {
              if (!trace.marker) trace.marker = {};
              trace.marker.line = {
                color: isDark ? "#62686e" : "#ffffff",
                width: 2
              };
            }
          });
        }

        return newFig;
      });
    },
  
  },
});

