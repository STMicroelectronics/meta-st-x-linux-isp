SYSROOT?=""
TARGET_BIN = x-linux-isp

CXXFLAGS += -std=c++17
LDFLAGS += -Wl,--hash-style=gnu

SRCS = x-linux-isp-tool.cc
OBJS = $(SRCS:.cc=.o)

all: $(TARGET_BIN)

$(TARGET_BIN): $(OBJS)
	$(CXX) $(LDFLAGS) -o $@ $^

$(OBJS): $(SRCS)
	$(CXX) $(CXXFLAGS) -c $^

clean:
	rm -rf $(OBJS) $(TARGET_BIN)
