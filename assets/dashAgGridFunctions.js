

var dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};

dagfuncs.rowSpan = function (params) {
    var Ref = params.data ? params.data.Ref : undefined;
    if (Ref === 'PBO') {
        // have all Aleksey Nemov cells in column athlete of height of 2 rows
        return 10;
    } else {
        // all other rows should be just normal
        return 1;
    }
}



var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dagcomponentfuncs.DCC_GraphClickData = function (props) {
    const {setData} = props;
    function setProps() {
        const graphProps = arguments[0];
        if (graphProps['clickData']) {
            setData(graphProps);
        }
    }
    return React.createElement(window.dash_core_components.Graph, {
        figure: props.value,
        setProps,
        style: {height: '100%'},
        config: {displayModeBar: false},
    });
};

