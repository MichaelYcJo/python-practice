
import Button from "components/Auth/Button";
import Icon from "components/Auth/Icon";
import Input from "components/Auth/Input";
import { FaFacebookF, FaInstagram, FaTwitter } from "react-icons/fa";
import VideoComponent from "components/Auth/VideoComponent";
import { ButtonContainer, ForgotPassword, HorizontalRule, IconsContainer, InputContainer, LoginContainer, LoginWith, WelcomeText } from './LoginContainer'


export const Login = () => {
    const FacebookBackground =
        "linear-gradient(to right, #0546A0 0%, #0546A0 40%, #663FB6 100%)";
    const InstagramBackground =
        "linear-gradient(to right, #A12AC4 0%, #ED586C 40%, #F0A853 100%)";
    const TwitterBackground =
        "linear-gradient(to right, #56C1E1 0%, #35A9CE 50%)";
    return (
        <>
            <VideoComponent />
            <LoginContainer>
                <WelcomeText>Welcome</WelcomeText>
                <InputContainer>
                    <Input type="text" placeholder="Email" />
                    <Input type="password" placeholder="Password" />
                </InputContainer>
                <ButtonContainer>
                    <Button content="Log In" />
                </ButtonContainer>
                <LoginWith>OR LOGIN WITH</LoginWith>
                <HorizontalRule />
                <IconsContainer>
                    <Icon color={FacebookBackground}>
                        <FaFacebookF />
                    </Icon>
                    <Icon color={InstagramBackground}>
                        <FaInstagram />
                    </Icon>
                    <Icon color={TwitterBackground}>
                        <FaTwitter />
                    </Icon>
                </IconsContainer>
                <ForgotPassword> Forgot Password ?</ForgotPassword>
            </LoginContainer>
        </>
    )
}

export default Login