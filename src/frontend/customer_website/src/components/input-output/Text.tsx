import React from 'react';

import '@assets/styles/input-output.css'

import Label from '@components/input-output/Label'



type InputProps = {
  id: string;
  name: string;
  value: string;
  placeholder: string;
  label_text: string;
};


function TextInput(props: InputProps) {
    const [text, setText] = React.useState(props.value);

    return (
        <>
            <Label for_id={props.id} text={props.label_text}/>
            <input
                type="text"
                id={props.id}
                name={props.name}
                value={text}
                placeholder={props.placeholder}
                onChange={e => setText(e.target.value)}
            />
        </>
    );
}

export default TextInput;
