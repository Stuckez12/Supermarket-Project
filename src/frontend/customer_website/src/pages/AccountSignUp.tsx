import { useForm } from 'react-hook-form';
import type { SubmitHandler } from 'react-hook-form';

import Text from '@components/input-output/Text.tsx'
import Password from '@components/input-output/Password.tsx'


type FormValues = {
  email: string;
  password: string;
  name: string;
  surname: string;
  gender: string;
  date_of_birth: string;
};

const AccountSignUp: React.FC = () => {

    const {
        handleSubmit,
        formState: { errors },
    } = useForm<FormValues>();

    const form_result: SubmitHandler<FormValues> = (data) => (
        console.log(data)
    );
    
    
    return <form action='https://localhost:50050/api/v1/account/register' onSubmit={handleSubmit(form_result)} >
        <Text id="sign-up-email-id" name="email" value="" placeholder="Username" label_text="Email: "/><br/>
        <Password id="sign-up-password-id" name="password" placeholder="Password" label_text="Password: "/><br/>
        <Text id="sign-up-name-id" name="name" value="" placeholder="Name" label_text="Name: "/><br/>
        <Text id="sign-up-surname-id" name="surname" value="" placeholder="Surname" label_text="Surname: "/><br/>
        <Text id="sign-up-gender-id" name="gender" value="" placeholder="Gender" label_text="Gender: "/><br/>
        <Text id="sign-up-dob-id" name="date_of_birth" value="" placeholder="Date of Birth" label_text="DOB: "/><br/>

        <button type="submit" className="mt-6 bg-blue-500 text-white p-2 rounded">
            Submit
        </button>
    </form>
}

export default AccountSignUp;
