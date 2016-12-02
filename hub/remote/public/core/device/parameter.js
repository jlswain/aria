import Component    from '../component';
import StateButton  from '../control/state-button';
import Slider       from '../control/slider';
import DataType     from './data-type';

class DeviceParameter extends Component {
    constructor (state, props) {
        super();
        this._state = state || '';
        this._props = props || {
            name        : '',
            dataType    : '',
            max         : 100,
            min         : 0,
            step        : 1
        };
        this._target = null;
    }

    render () {
        var option = optionOf(this._props.dataType, this._state);

        if (this._target) { this._target.remove(); }
        this._$el.empty();

        switch (this._props.dataType) {
            case DataType.Binary:
                this._target = new StateButton(option, ['On', 'Off']);
                this._target.change((v) => {
                    this._state = valueOf(this._props.dataType, v);
                    this._changed();
                });
                break;
            case DataType.Integer:
                this._target = new Slider(option, {
                    max     : this._props.max,
                    min     : this._props.min,
                    step    : this._props.step,
                    round   : true
                });
                this._target.change((v) => {
                    this._state = v;
                    this._changed();
                });
                break;
            default:
                this._target = null;
                break;
        }

        if (this._target) {
            this._$el.append(
                this._target
                    .state(this._state)
                    .render()
                    .$el()
            );
        }
        return this;
    }
    remove () {
        if (this._target) { this._target.remove(); }
        super.remove();
    }
}

function optionOf (dataType, val) {
    switch (dataType) {
        case DataType.Binary:
            return val ? 'On' : 'Off';
        default:
            return val;
    }
}

function valueOf (dataType, val) {
    switch (dataType) {
        case DataType.Binary:
            return val === 'On' ? 1 : 0;
        default:
            return val;
    }
}


export default DeviceParameter;
