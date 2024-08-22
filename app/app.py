from flask import Flask, Response
from obswebsocket import obsws, requests # noqa: E402
from dotenv import load_dotenv
import os

# Parameters
load_dotenv()
obs_host = os.getenv("OBS_HOST")
obs_port = os.getenv("OBS_PORT")
obs_password = os.getenv("OBS_PASSWORD")
listen_port = os.getenv("LISTEN_PORT")

app = Flask(__name__)

def format_stats_metrics(stats):
    """
    Format the OBS stats into Prometheus metrics format.
    """
    metrics = []
    data = stats.datain
    
    # Current FPS being rendered
    metrics.append(f"obs_active_fps {data['activeFps']}")

    # Available disk space on the device being used for recording storage
    metrics.append(f"obs_available_disk_space {data['availableDiskSpace']}") 
    
    # Average time in milliseconds that OBS is taking to render a frame
    metrics.append(f"obs_average_frame_render_time {data['averageFrameRenderTime']}")
    
    # Current CPU usage in percent
    metrics.append(f"obs_cpu_usage {data['cpuUsage']}")
    
    # Memory usage
    metrics.append(f"obs_memory_usage {data['memoryUsage']}") 
    
    # Number of frames skipped by OBS in the output thread
    metrics.append(f"obs_output_skipped_frames {data['outputSkippedFrames']}")
    
    # Total number of frames outputted by the output thread
    metrics.append(f"obs_output_total_frames {data['outputTotalFrames']}")
    
    # Number of frames skipped by OBS in the render thread
    metrics.append(f"obs_render_skipped_frames {data['renderSkippedFrames']}")
    
    # Total number of frames outputted by the render thread
    metrics.append(f"obs_render_total_frames {data['renderTotalFrames']}")
    
    # Total number of messages received by obs-websocket from the client
    metrics.append(f"obs_websocket_session_incoming_messages {data['webSocketSessionIncomingMessages']}")

    # Total number of messages sent by obs-websocket from the client
    metrics.append(f"obs_websocket_session_outgoing_messages {data['webSocketSessionOutgoingMessages']}\n")
    
    return "\n".join(metrics)

def format_stream_status_metrics(stream_status):
    """
    Format the OBS Stream Status into Prometheus metrics format.
    """
    metrics = []
    data = stream_status.datain
    
    # Whether the output is active (Boolean)
    if data['outputActive']:
        metrics.append(f"obs_stream_status_output_active 1")
    else:
        metrics.append(f"obs_stream_status_output_active 0")

    # Number of bytes sent by the output (Number)
    metrics.append(f"obs_stream_status_output_bytes {data['outputBytes']}")

    # Congestion of the output (Number)
    metrics.append(f"obs_stream_status_output_congestion {data['outputCongestion']}")

    # Current duration in milliseconds for the output (Number)
    metrics.append(f"obs_stream_status_output_duration {data['outputDuration']}")

    # Whether the output is currently reconnecting (Boolean)
    #metrics.append(f"obs_stream_status_output_reconnecting {data['outputReconnecting']}")

    # Number of frames skipped by the output's process (Number)
    metrics.append(f"obs_stream_status_output_skipped_frames {data['outputSkippedFrames']}")

    # Current formatted timecode string for the output (String)
    #metrics.append(f"obs_stream_status_output_timecode {data['outputTimecode']}")

    # Total number of frames delivered by the output's process (Number)
    metrics.append(f"obs_stream_status_output_total_frames {data['outputTotalFrames']}\n")
    
    return "\n".join(metrics)


@app.route('/metrics', methods=['GET'])

def get_stats():
    try:
        # Initialize the obsws client
        ws = obsws(obs_host, obs_port, obs_password)
        ws.connect()  # Connect to the OBS WebSocket server
        stats = ws.call(requests.GetStats()) 
        stream_status = ws.call(requests.GetStreamStatus())
        ws.disconnect() 

        # Format the metrics for Prometheus
        prometheus_metrics = format_stats_metrics(stats)
        prometheus_metrics += format_stream_status_metrics(stream_status)
        
        return Response(prometheus_metrics, mimetype='text/plain')
    except Exception as e:
        return Response(f"# Error: {str(e)}", mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=listen_port)
