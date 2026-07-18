import AppRouter from "./routes/AppRouter";
import { ToastProvider } from "./components/ui";

export default function App({ initialData }) {
  return (
    <ToastProvider>
      <AppRouter initialData={initialData} />
    </ToastProvider>
  );
}
