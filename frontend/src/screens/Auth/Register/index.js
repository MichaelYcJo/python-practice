
import Button from "components/Auth/Button";
import Input from "components/Auth/Input";
import { ButtonContainer, InputContainer, EmailWrapper, EmailInput, EmailAuthBtn, RegisterContainer, WelcomeText } from './RegisterContainer'
import './register.css'

export const Login = () => {

    return (
        <RegisterContainer>
            <WelcomeText>Register</WelcomeText>

            <InputContainer>
                <EmailWrapper>
                    <EmailInput type="text" placeholder="Email" />
                    <EmailAuthBtn >Check Email</EmailAuthBtn>
                </EmailWrapper>
                <Input type="password" placeholder="Password" />
                <Input type="password" placeholder="Confirm Password" />
                <Input type="text" placeholder="Name" />
            </InputContainer>
            <ButtonContainer>
                <Button content="Register" />
            </ButtonContainer>

        </RegisterContainer>
    )
}

export default Login