type LabelProps = {
  for_id: string;
  text: string;
};

function Label({ for_id, text }: LabelProps) {
    return (
        <label htmlFor={for_id} className="Label">{text}</label>
    );
}

export default Label;