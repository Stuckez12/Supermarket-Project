import React from 'react';

import '@assets/styles/input-output.css'

import Label from '@components/input-output/Label'



type InputProps = {
  id: string;
  name: string;
  placeholder: string;
  label_text: string;
};


function PasswordInput(props: InputProps) {

    return (
        <>
            <Label for_id='fname' text={props.label_text}/>
            <input
                type="password"
                id={props.id}
                name={props.name}
                placeholder={props.placeholder}
            />
        </>
    );
}

export default PasswordInput;
