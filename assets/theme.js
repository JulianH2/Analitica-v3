window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    switch_graph_theme: function (theme, ids, figures) {
      const currentTheme = theme || "dark";

      if (!figures || !Array.isArray(figures)) {
        return window.dash_clientside.no_update;
      }

      const isDark = currentTheme === "dark";
      const templateName = isDark ? "zam_dark" : "zam_light";

      const colors = {
        dark: {
          text: "#e8eaed",
          secondary: "#9ca3af",
          tooltipBg: "#2d3748",
          gridColor: "#4a5a68",
          annotationBg: "rgba(45, 55, 72, 0.9)",
        },
        light: {
          text: "#1d1d1b",
          secondary: "#6b7280",
          tooltipBg: "#ffffff",
          gridColor: "#e5e7eb",
          annotationBg: "rgba(255, 255, 255, 0.9)",
        },
      };

      const c = isDark ? colors.dark : colors.light;

      return figures.map((fig) => {
        if (!fig) return null;

        const newFig = JSON.parse(JSON.stringify(fig));
        if (!newFig.layout) newFig.layout = {};

        newFig.layout.template = templateName;
        newFig.layout.paper_bgcolor = "rgba(0,0,0,0)";
        newFig.layout.plot_bgcolor = "rgba(0,0,0,0)";

        newFig.layout.font = {
          color: c.text,
          family: "'Nexa', -apple-system, BlinkMacSystemFont, sans-serif",
          size: 12,
        };

        newFig.layout.hoverlabel = {
          bgcolor: c.tooltipBg,
          bordercolor: c.gridColor,
          font: {
            color: c.text,
            size: 13,
            family: "'Nexa', sans-serif",
          },
        };

        if (newFig.layout.annotations && Array.isArray(newFig.layout.annotations)) {
          newFig.layout.annotations = newFig.layout.annotations.map((ann) => ({
            ...ann,
            font: {
              ...ann.font,
              color: c.text,
            },
            bgcolor: c.annotationBg,
            bordercolor: c.gridColor,
          }));
        }

        if (newFig.layout.xaxis) {
          newFig.layout.xaxis = {
            ...newFig.layout.xaxis,
            gridcolor: c.gridColor,
            color: c.text,
            tickfont: { color: c.secondary },
            titlefont: { color: c.text },
          };
        }

        if (newFig.layout.yaxis) {
          newFig.layout.yaxis = {
            ...newFig.layout.yaxis,
            gridcolor: c.gridColor,
            color: c.text,
            tickfont: { color: c.secondary },
            titlefont: { color: c.text },
          };
        }

        if (newFig.layout.legend) {
          newFig.layout.legend = {
            ...newFig.layout.legend,
            font: { color: c.text },
            bgcolor: "rgba(0,0,0,0)",
          };
        }

        if (newFig.data && Array.isArray(newFig.data)) {
          newFig.data = newFig.data.map((trace) => {
            const newTrace = { ...trace };

            if (trace.type === "indicator") {
              if (newTrace.number) {
                newTrace.number = {
                  ...newTrace.number,
                  font: {
                    ...newTrace.number.font,
                    color: c.text,
                  },
                };
              }

              if (newTrace.title) {
                newTrace.title = {
                  ...newTrace.title,
                  font: {
                    ...newTrace.title.font,
                    color: c.text,
                  },
                };
              }

              if (newTrace.gauge) {
                newTrace.gauge = {
                  ...newTrace.gauge,
                  bgcolor: isDark
                    ? "rgba(255,255,255,0.05)"
                    : "rgba(0,0,0,0.05)",
                  bordercolor: c.gridColor,
                };

                if (newTrace.gauge.axis) {
                  newTrace.gauge.axis = {
                    ...newTrace.gauge.axis,
                    tickfont: {
                      color: c.secondary,
                      size: 10,
                    },
                  };
                }

                if (newTrace.gauge.bar) {
                  newTrace.gauge.bar = {
                    ...newTrace.gauge.bar,
                  };
                }
              }

              if (newTrace.delta) {
                newTrace.delta = {
                  ...newTrace.delta,
                  font: {
                    color: c.text,
                  },
                };
              }
            }

            if (trace.type === "pie") {
              if (!newTrace.marker) newTrace.marker = {};
              newTrace.marker.line = {
                color: isDark ? "#1f2937" : "#ffffff",
                width: 2,
              };

              newTrace.textfont = {
                color: c.text,
                size: 12,
              };
            }

            if (trace.type === "scatter") {
              if (newTrace.marker) {
                newTrace.marker = {
                  ...newTrace.marker,
                  line: {
                    ...newTrace.marker.line,
                    color: isDark ? "#1f2937" : "#ffffff",
                    width: 1,
                  },
                };
              }
            }

            if (trace.type === "bar") {
              if (newTrace.marker) {
                newTrace.marker = {
                  ...newTrace.marker,
                  line: {
                    color: isDark ? "#1f2937" : "#ffffff",
                    width: 1,
                  },
                };
              }
            }

            return newTrace;
          });
        }

        if (newFig.layout.shapes && Array.isArray(newFig.layout.shapes)) {
          newFig.layout.shapes = newFig.layout.shapes.map((shape) => ({
            ...shape,
            line: {
              ...shape.line,
              color: shape.line?.color || c.gridColor,
            },
          }));
        }

        return newFig;
      });
    },
  },
});
