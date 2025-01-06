import api from '../api';
import { jwtDecode } from "jwt-decode";
import { ACCESS_TOKEN } from "../constants";

export const formatDate = (dateString) => {
    const date = new Date(dateString);

    const optionsDate = { year: 'numeric', month: '2-digit', day: '2-digit' };
    const optionsTime = { hour: '2-digit', minute: '2-digit' };

    const formattedDate = date.toLocaleDateString('de-DE', optionsDate);
    const formattedTime = date.toLocaleTimeString('de-DE', optionsTime);

    return `${formattedDate} ${formattedTime}`;
};

export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(amount);
};

export const getRequest = async (url, setIsLoading) => {
    if (setIsLoading) setIsLoading(true);

    try {
        const response = await api.get(url);
        return response.data;
    } catch (e) {
        throw new Error(e.message);
    } finally {
        if (setIsLoading) setIsLoading(false);
    }
};

export const getError = (error) => {
    const data = error.response.data;
    if (!data) {
        return error.message;
    }

    if ("non_field_errors" in data) {
        return data.non_field_errors[0];
    }

    const problem = Object.values(data).find(data1 => data1.length > 0)?.[0]
    if (problem) return problem;
    return error.message;
}

export const isAdmin = () => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
        try {
            const decodedToken = jwtDecode(token);
            return decodedToken.is_staff;
        } catch (error) {
            console.error("Fehler beim Dekodieren des Tokens:", error);
            return false;
        }
    }
    return false;
};
