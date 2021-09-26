import axios from "axios";

const callApi = async (method, path, data, jwt, params = {}) => {
    const headers = {
        Authorization: `Bearer ${jwt}`,
        "Content-Type": "application/json"
    };
    const baseUrl = `http://127.0.0.1:8000/api/v1`;
    const fullUrl = `${baseUrl}${path}`;
    if (method === "get" || method === "delete") {
        return axios[method](fullUrl, { headers, params });
    } else {
        if (path === "/accounts/register/") {
            return axios[method](fullUrl, data);
        } else {
            return axios[method](fullUrl, data, { headers });
        }
    }
};

const apiList = {
    createAccount: form => callApi("post", "/accounts/register/", form),
    login: form => callApi("post", "/accounts/login/", form),
    userProfile: jwt => callApi("get", "/accounts/profile/", null, jwt),

};

export default apiList;
