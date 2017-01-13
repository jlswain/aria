import $            from 'jquery';
import Component    from '../component';

import './field.css';

class Field extends Component {
    constructor (state, props) {
        super();
        props = props || {};
        this._props = {
            label       : props.label    || '',
            editable    : props.editable || false
        };
        this._state = state || '';

        this._$label = $('<div>').addClass('field-label');
        this._$value = $('<div>').addClass('field-value');
    }
    render () {
        this._$label.text(this._props.label);
        this._$value.text(this._state).removeClass('field-editable');

        if (this._props.editable) {
            this._$value
                .addClass('field-editable')
                .change(this._changed.bind(this));
        }

        this._$el
            .empty()
            .addClass('field-body')
            .append([this._$label, this._$value]);


        return this;
    }
}

export default Field;
