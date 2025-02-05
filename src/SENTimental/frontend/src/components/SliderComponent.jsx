import { useId, useState } from "react";
import PropTypes from 'prop-types';

export const SliderComponent = ( { min = 0, max = 100, step = 1, bindTo, onChange = () => {}, thresholds = [] } ) => {
    const [_value, _setValue] = bindTo;
    const id = useId()

    function handleChange( evt ) {
        _setValue( evt.target.value );
        onChange( evt.target.value );
    }

    function valueColor( _value ) {
        let _color = null;
        if( thresholds && thresholds.length > 0 ) {
            for( const boundary of thresholds.sort( (a,b) => a.bound - b.bound ) ) {
                if(  boundary.bound > _value )
                    break;
                _color = boundary.color;
            };
        }
        return _color;
    }

    const tickMarks = [...Array(step+1).keys()].map( (v,i) => {
        const _color = valueColor( i*step )
        if( _color )
            return <span style={{ color: _color, backgroundColor: _color }} key={i}>|</span>
        return <span key={i}>|</span>
    } );

    

    return <div className="flex flex-col w-full">
        <div className="flex w-full justify-between px-2">
            <span>Negative</span>
            <span className="flex-grow text-center">Neutral</span>
            <span>Positive</span>
        </div>
        <input className="inline-block flex-grow range" id={id} type="range" min={min} max={max} step={step} value={_value} onChange={handleChange} />
        <div className="flex w-full justify-between px-2 text-xs">
            {tickMarks}
        </div>
    </div>
}

SliderComponent.propTypes = {
    min: PropTypes.number,
    max: PropTypes.number,
    step: PropTypes.number,
    bindTo: PropTypes.array,
    onChange: PropTypes.func,
    thresholds: PropTypes.array
};