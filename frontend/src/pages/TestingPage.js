import ProcessPlotButton from "../components/ProcessPlotButton";

export default function TestingPage() {
  return (
    <div className="p-4 space-y-6">
      <ProcessPlotButton processName="mixing" />
      <ProcessPlotButton processName="coating" />
      <ProcessPlotButton processName="drying" />
    </div>
  );
}
